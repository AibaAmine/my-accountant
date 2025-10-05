# chat/views.py
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .serializers import (
    ChatMessageSerializer,
    ChatRoomSerializer,
    ChatRoomCreateSerializer,
    ChatMessageUpdateSerializer,
    ChatMessageDeleteSerializer,
    ChatFileUploadSerializer,
)
from .models import ChatRooms, ChatMessages, ChatMembers, UserRoomLastSeen
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser
from django.http import FileResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from django.db import models
from accounts.models import User
from accounts.serializers import CustomUserDetailsSerializer

from django.db.models import Prefetch, Count

User = get_user_model()


#!missing endpoints
# optional : add api endpoint to delete dm rooms
# Room Members Count - GET /api/chat/rooms/{id}/members/count/ for UI badges

# Unread Messages Count - GET /api/chat/unread-count/ for notifications


# api endpoint to list available users that authenticated user can message to add members to a room
class AvailableUserListAPIView(generics.ListAPIView):
    serializer_class = CustomUserDetailsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    pagination_class = PageNumberPagination
    page_size = 20
    search_fields = ["full_name", "email"]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "client":
            return User.objects.filter(user_type="accountant").exclude(id=user.id)
        if user.user_type == "accountant":
            return User.objects.all().exclude(id=user.id)

        if user.user_type == "academic":
            return User.objects.filter(
                user_type__in=["accountant", "academic"]
            ).exclude(id=user.id)
        return User.objects.none()


# user Group Chat Rooms
class GroupChatRoomListAPIView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    # add the request obj to the serializer
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user = self.request.user

        return (
            ChatRooms.objects.filter(members__user_id=user, is_dm=False)
            .exclude(room_name__startswith="dm_")
            .select_related(
                "creator"
            )  # Prefetch creator data(we use select_related for foreign key attributs (performing joins))
            .prefetch_related(
                # Prefetch user's last seen data for unread messages((we use prefetch_related to fetch for ex room.members...many to many fields...etc))
                Prefetch(
                    "user_last_seen",
                    queryset=UserRoomLastSeen.objects.filter(user=user),
                    to_attr="prefetched_user_last_seen",
                )
            )
            .annotate(
                # Annotate counts to avoid N+1 queries
                message_count_annotated=Count("messages"),
                members_count_annotated=Count("members"),
                last_message_time=models.Max("messages__sent_at"),
            )
            .order_by("-last_message_time")
        )


# user Direct Message Rooms
class DirectMessageRoomListAPIView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user = self.request.user
        return (
            ChatRooms.objects.filter(members__user_id=user, is_dm=True)
            .select_related("creator")
            .prefetch_related(
                Prefetch(
                    "user_last_seen",
                    queryset=UserRoomLastSeen.objects.filter(user=user),
                    to_attr="prefetched_user_last_seen",
                )
            )
            .annotate(
                message_count_annotated=Count("messages"),
                members_count_annotated=Count("members"),
                last_message_time=models.Max("messages__sent_at"),
            )
            .order_by("-last_message_time")
        )


# create group chat room
class GroupChatRoomCreateAPIView(generics.CreateAPIView):

    queryset = ChatRooms.objects.all()
    serializer_class = ChatRoomCreateSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        user = self.request.user
        if not can_create_rooms(user):
            raise PermissionDenied("You do not have permission to create chat rooms.")
        # Create the room and then add the creator as a member
        room = serializer.save(creator=user)
        # Ensure the creator is a room member
        ChatMembers.objects.create(room_id=room, user_id=user)


# Chat group Rooms Retrieve, Update, Delete
class GroupChatRoomRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatRooms.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "room_id"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        user = self.request.user

        return (
            ChatRooms.objects.filter(members__user_id=user)
            .select_related("creator")
            .prefetch_related(
                Prefetch(
                    "user_last_seen",
                    queryset=UserRoomLastSeen.objects.filter(user=user),
                    to_attr="prefetched_user_last_seen",
                )
            )
            .annotate(
                message_count_annotated=Count("messages"),
                members_count_annotated=Count("members"),
            )
        )

    def get_object(self):
        obj = super().get_object()

        if not can_access_rooms(self.request.user):
            raise PermissionDenied("You do not have access to chat rooms.")
        return obj

    def perform_update(self, serializer):
        serializer.save(creator=self.request.user)

    def perform_destroy(self, instance):
        # Ensure the user is the creator before deleting
        if instance.creator == self.request.user:
            instance.delete()
        else:
            raise PermissionError("You do not have permission to delete this room.")


class ChatRoomAddMemberAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRooms, room_id=room_id)

        if room.is_dm:
            raise PermissionDenied("You cannot add members to a direct message room.")

        #! change this for admin users
        if room.creator != request.user:
            raise PermissionDenied(
                "You do not have permission to add members to this room."
            )

        target_user_id = request.data.get("user_id")

        target_user = get_object_or_404(User, id=target_user_id)

        if target_user.user_type == "client":
            return Response(
                {"detail": "You cannot add a client to this room."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if room.members.filter(user_id=target_user).exists():
            return Response(
                {
                    "detail": f"{target_user.full_name} is already a member of this room."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        ChatMembers.objects.create(room_id=room, user_id=target_user)

        # Broadcast member added event to all room users
        channel_layer = get_channel_layer()
        room_group_name = f"chat_{room.room_id}"

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "member.added",
                "user_id": str(target_user.id),
                "full_name": target_user.full_name,
                "room_id": str(room.room_id),
                "added_by": str(request.user.id),
                "added_by_name": request.user.full_name,
            },
        )
        serializer = ChatRoomSerializer(room)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatRoomRemoveMemberAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id, user_id_to_remove):
        room = get_object_or_404(ChatRooms, room_id=room_id)

        if room.creator != request.user:
            raise PermissionDenied(
                "You do not have permission to remove members from this room."
            )

        if not room.is_private:
            return Response(
                {"detail": "Members can only be removed from private chat rooms."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = get_object_or_404(User, id=user_id_to_remove)

        if target_user == request.user:
            return Response(
                {
                    "detail": "You cannot remove yourself from a room you created. Delete the room instead."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not room.members.filter(user_id=target_user).exists():
            return Response(
                {"detail": f"{target_user.full_name} is not a member of this room."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room.members.filter(user_id=target_user).delete()

        # Broadcast member removed event to all room users
        channel_layer = get_channel_layer()
        room_group_name = f"chat_{room.room_id}"

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "member.removed",
                "user_id": str(target_user.id),
                "full_name": target_user.full_name,
                "room_id": str(room.room_id),
                "removed_by": str(request.user.id),
                "removed_by_name": request.user.full_name,
            },
        )

        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)


# creating fetching dm rooms
class DirectMessageRoomAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        current_user = request.user
        target_user_id = request.data.get("target_user_id")

        target_user = get_object_or_404(User, id=target_user_id)

        if current_user.id == target_user.id:
            return Response(
                {"error": "Cannot create or direct message with yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not can_users_communicate(current_user, target_user):
            return Response(
                {"error": "You cannot message this user"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate room name for direct messages
        # we use sorted to ensures that the room name is the same
        user_ids = sorted([str(current_user.id), str(target_user.id)])

        dm_room_name = f"dm_{user_ids[0]}_{user_ids[1]}"

        # try to find and existing private room with these two members
        try:
            dm_room = ChatRooms.objects.get(
                room_name=dm_room_name, is_private=True, is_dm=True
            )

        except ChatRooms.DoesNotExist:
            dm_room = ChatRooms.objects.create(
                room_name=dm_room_name,
                description=f"Direct message between {current_user.full_name} and {target_user.full_name}",
                is_private=True,
                is_dm=True,
                creator=current_user,
            )

            # Add the two users as members
            ChatMembers.objects.create(room_id=dm_room, user_id=current_user)
            ChatMembers.objects.create(room_id=dm_room, user_id=target_user)

        serializer = ChatRoomSerializer(dm_room)

        return Response(serializer.data, status=status.HTTP_200_OK)


#!add pagination and search options
class RoomMemberListAPIView(generics.ListAPIView):

    serializer_class = CustomUserDetailsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 20
    filter_backends = [SearchFilter]
    search_fields = ["full_name"]

    def get_queryset(self):
        room_id = self.kwargs.get("room_id")
        room = get_object_or_404(ChatRooms, room_id=room_id)

        if not room.members.filter(user_id=self.request.user).exists():
            raise PermissionDenied("You are not a member of this room.")

        return User.objects.filter(chat_memberships__room_id=room)


class RoomMessageListAPIView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    page_size = 20
    ordering = ["-sent_at"]
    filter_backends = [SearchFilter]
    search_fields = ["content"]

    def get_queryset(self):
        room_id = self.kwargs.get("room_id")
        room = get_object_or_404(ChatRooms, room_id=room_id)

        if not room.members.filter(user_id=self.request.user).exists():
            raise PermissionDenied("You are not a member of this room.")

        return room.messages.all()


class RoomMembersCountAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(ChatRooms, room_id=room_id)

        if not room.members.filter(user_id=request.user).exists():
            raise PermissionDenied("You are not a member of this room.")

        return Response({"members_count": room.members.count()})


class ChatMessageUpdateAPIView(generics.UpdateAPIView):
    queryset = ChatMessages.objects.all()
    serializer_class = ChatMessageUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "message_id"

    def get_queryset(self):
        user = self.request.user
        return ChatMessages.objects.filter(sender=user, is_deleted=False)

    def get_object(self):
        obj = super().get_object()
        if obj.sender != self.request.user:
            raise PermissionDenied("You do not have permission to edit this message.")
        if obj.is_deleted:
            raise PermissionDenied("You cannot edit a deleted message.")

        if not obj:
            raise PermissionDenied("Message not found.")
        return obj

    def perform_update(self, serializer):
        updated_message = serializer.save()
        # Notify channel layer that a message was edited
        room_group_name = f"chat_{updated_message.room.room_id}"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "message_edited",
                "message_id": str(updated_message.message_id),
                "new_content": updated_message.content,
                "edited_at": updated_message.edited_at.isoformat(),
                "room_id": str(updated_message.room.room_id),
                "sender_id": str(updated_message.sender.id),
                "sender_full_name": updated_message.sender.full_name,
            },
        )


#!add proper responses for permission checks
class ChatMessageDeleteAPIView(generics.DestroyAPIView):
    queryset = ChatMessages.objects.all()
    serializer_class = ChatMessageDeleteSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "message_id"

    def get_queryset(self):
        return ChatMessages.objects.filter(sender=self.request.user, is_deleted=False)

    def get_object(self):
        obj = super().get_object()
        if obj.sender != self.request.user:
            raise PermissionDenied("You do not have permission to delete this message.")

        if not obj or obj.is_deleted:
            raise PermissionDenied("Message not found or already deleted.")
        return obj

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.content = "This message has been deleted"
        instance.edited_at = datetime.now()
        instance.save()
        # Notify channel layer that a message was deleted
        room_group_name = f"chat_{instance.room.room_id}"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "message_deleted",
                "message_id": str(instance.message_id),
                "room_id": str(instance.room.room_id),
                "edited_at": instance.edited_at.isoformat(),
            },
        )


class ChatFileUploadAPIView(views.APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRooms, room_id=room_id)

        if not room.members.filter(user_id=request.user).exists():
            raise PermissionDenied("You are not a member of this room.")

        serializer = ChatFileUploadSerializer(data=request.data)

        if serializer.is_valid():
            msg = serializer.save(sender=request.user, room=room, message_type="file")
            # broadcast the file-message to WS group
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                f"chat_{room_id}",
                {
                    "type": "chat_message",
                    "message_id": str(msg.message_id),
                    "message": msg.file.url,
                    "sender_id": str(request.user.id),
                    "sender_full_name": request.user.full_name,
                    "timestamp": msg.sent_at.isoformat(),
                    "message_type": "file",
                },
            )
            return Response({"file_url": msg.file.url}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarkRoomAsReadAPIView(views.APIView):
    """API endpoint to manually update user's last seen timestamp for a room"""

    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(ChatRooms, room_id=room_id)

        # Check if user is a member of the room
        if not room.members.filter(user_id=request.user).exists():
            raise PermissionDenied("You are not a member of this room.")

        from django.utils import timezone

        # Update or create last seen record using your related_name
        last_seen, created = room.user_last_seen.get_or_create(
            user=request.user, defaults={"last_seen_at": timezone.now()}
        )

        if not created:
            last_seen.last_seen_at = timezone.now()
            last_seen.save()

        return Response(
            {"message": "Last seen updated successfully"}, status=status.HTTP_200_OK
        )


class UnreadMessageCountAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        unread_count = 0

        # Count unread messages across all rooms
        user_rooms = ChatRooms.objects.filter(members__user_id=user)

        for room in user_rooms:
            try:
                last_seen = room.user_last_seen.get(user=user)
                unread_count += (
                    room.messages.filter(
                        sent_at__gt=last_seen.last_seen_at, is_deleted=False
                    )
                    .exclude(sender=user)
                    .count()
                )
            except:
                unread_count += (
                    room.messages.filter(is_deleted=False).exclude(sender=user).count()
                )

        return Response({"unread_count": unread_count})


# HELPER FUNCTIONS FOR ROLES CHECKING


def can_users_communicate(user1, user2):
    """Check if two users can communicate based on their roles"""
    role1 = user1.user_type
    role2 = user2.user_type

    # Accountants can talk to everyone
    if role1 == "accountant" or role2 == "accountant":
        return True

    if role1 == "academic" and role2 == "academic":
        return True

    return False


def can_create_rooms(user):
    """Only accountants can create rooms"""
    return user.user_type == "accountant"


def can_access_rooms(user):
    """Clients cannot access rooms at all"""
    return user.user_type != "client"
