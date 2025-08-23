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
)
from .models import ChatRooms, ChatMessages
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django.http import FileResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from django.db import models
from accounts.models import User
from accounts.serializers import CustomUserDetailsSerializer

User = get_user_model()


#!missing endpoints
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
            return User.objects.filter(user_type="accountant").exclude(id=user.id)
        return User.objects.none()


# user Group Chat Rooms
class GroupChatRoomListAPIView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return (
            ChatRooms.objects.filter(
                members__user_id=user,
                is_dm=False,
            )
            .exclude(room_name__startswith="dm_")  # list only rooms
            .annotate(  # this find the most recent message from any user in that room
                last_mesasge_time=models.Max("messages__sent_at")
            )
            .order_by("-last_message_time")
        )

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if not can_access_rooms(user):
            return Response(
                {"detail": "You do not have access to chat rooms."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)


# user Direct Message Rooms
class DirectMessageRoomListAPIView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            ChatRooms.objects.filter(
                members__user_id=user,
                is_dm=True,
            )
            .annotate(last_message_time=models.Max("messages__sent_at"))
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
        serializer.save(creator=user)


# Chat Room Retrieve, Update, Delete
class ChatRoomRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChatRooms.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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

        if room.creator != request.user:
            raise PermissionDenied(
                "You do not have permission to add members to this room."
            )

        if not room.is_private:
            return Response(
                {"detail": "Members can only be added to private chat rooms."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user_id = request.data.get("user_id")
        if not target_user_id:
            return Response(
                {"detail": "User ID to add is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = get_object_or_404(User, id=target_user_id)

        # Check if the target user can be added
        if not can_users_communicate(request.user, target_user):
            return Response(
                {
                    "detail": "This user cannot be added to the room based on role restrictions."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if room.members.filter(id=target_user.id).exists():
            return Response(
                {"detail": f"{target_user.username} is already a member of this room."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room.members.add(target_user)

        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChatRoomRemoveMemberAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

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

        if not room.members.filter(id=target_user.id).exists():
            return Response(
                {"detail": f"{target_user.username} is not a member of this room."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        room.members.remove(target_user)

        serializer = ChatRoomSerializer(room)
        return Response(serializer.data, status=status.HTTP_200_OK)


# creating getting dm rooms
class DirectMessageRoomAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):

        current_user = request.user
        target_user_id = request.data.get("target_user_id")

        if not target_user_id:
            return Response(
                {"error": "target_user_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = get_object_or_404(User, id=target_user_id)

        if current_user.id == target_user.id:
            return Response(
                "Cannot create or direct message with yourself.",
                status.HTTP_400_BAD_REQUEST,
            )

        if not can_users_communicate(current_user, target_user):
            return Response(
                {"error": "You cannot message this user"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Generate rooom name for direct messages
        # we use sorted to ensures that the room name is the same
        user_ids = sorted([str(current_user.id), str(target_user.id)])

        dm_room_name = f"dm_{user_ids[0]}_{user_ids[1]}"

        # try to find and existing private room with these two members
        try:
            dm_room = ChatRooms.objects.get(room_name=dm_room_name, is_private=True)

            dm_room.members.set([current_user, target_user])

        except ChatRooms.DoesNotExist:
            dm_room = ChatRooms.objects.create(
                room_name=dm_room_name,
                description=f"Direct message between {current_user.username} and {target_user.username}",
                is_private=True,
                is_dm=True,
                creator=current_user,
            )

            dm_room.members.set([current_user, target_user])
            print(f"Created new DM room :{dm_room_name}")

        serializer = ChatRoomSerializer(dm_room)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RoomMemberListAPIView(generics.ListAPIView):

    serializer_class = CustomUserDetailsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        room_id = self.kwargs.get("room_id")
        room = get_object_or_404(ChatRooms, room_id=room_id)

        if not room.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a member of this room.")

        return room.members.all()


# add search and ordering and pagination
class RoomMessageListAPIView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = PageNumberPagination
    page_size = 20
    ordering = ["-sent_at"]
    filter_backends = [SearchFilter]
    search_fields = ["content"]

    def get_queryset(self):
        room_id = self.kwargs.get("room_id")
        room = get_object_or_404(ChatRooms, room_id=room_id)

        if not room.members.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You are not a member of this room.")

        return room.messages.all()


class ChatMessageUpdateAPIView(generics.UpdateAPIView):
    queryset = ChatMessages.objects.all()
    serializer_class = ChatMessageUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "message_id"

    def get_queryset(self):
        return ChatMessages.objects.filter(sender=self.request.user, is_deleted=False)

    def perform_update(self, serializer):
        updated_message = serializer.save()

        room_group_name = f"chat_{updated_message.room.room_name}"

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
                "sender_username": updated_message.sender.username,
            },
        )


class ChatMessageDeleteAPIView(generics.DestroyAPIView):
    queryset = ChatMessages.objects.all()
    serializer_class = ChatMessageDeleteSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = "message_id"

    def get_queryset(self):
        return ChatMessages.objects.filter(sender=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.content = "This message has been deleted"
        instance.edited_at = datetime.now()
        instance.save()

        room_group_name = f"chat_{instance.room.room_name}"
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                "type": "message_deleted",
                "message_id": str(instance.message_id),
                "room_id": str(instance.room.room_id),
            },
        )


# HELPER FUNCTIONS FOR ROLES CHECKING
def can_users_communicate(user1, user2):
    """Check if two users can communicate based on their roles"""
    role1 = user1.user_type
    role2 = user2.user_type

    # Accountants can talk to everyone
    if role1 == "accountant" or role2 == "accountant":
        return True

    if role1 == "student" and role2 == "student":
        return True

    return False


def can_create_rooms(user):
    """Only accountants can create rooms"""
    return user.user_type == "accountant"


def can_access_rooms(user):
    """Clients cannot access rooms at all"""
    return user.user_type != "client"


