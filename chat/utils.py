from django.db import models
from .models import ChatRooms, ChatMembers
from accounts.models import User


def create_or_get_dm_room(user1, user2):
    """
    Creates or retrieves a DM room between two users.
    Returns the ChatRooms instance.
    """
    # Check if a DM room already exists between these users
    existing_room = (
        ChatRooms.objects.filter(is_dm=True, members__user_id__in=[user1.id, user2.id])
        .annotate(member_count=models.Count("members"))
        .filter(member_count=2)
        .first()
    )

    if existing_room:
        # Verify both users are members
        member_users = existing_room.members.values_list("user_id", flat=True)
        if set(member_users) == {user1.id, user2.id}:
            return existing_room

    # Create new DM room
    room_name = f"DM: {user1.full_name} & {user2.full_name}"

    dm_room = ChatRooms.objects.create(
        room_name=room_name,
        description=f"Direct message between {user1.full_name} and {user2.full_name}",
        is_private=True,
        is_dm=True,
        creator=user1,
    )

    # Add both users as members
    ChatMembers.objects.create(room_id=dm_room, user_id=user1)
    ChatMembers.objects.create(room_id=dm_room, user_id=user2)

    return dm_room
