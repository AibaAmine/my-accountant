from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):


    def populate_user(self, request, sociallogin, data):
        # Let default adapter set first_name and last_name
        user = super().populate_user(request, sociallogin, data)
        # Use full name if available in data (e.g., 'name' from Google)
        full = data.get("name")
        if full:
            user.full_name = full
        else:
            # Fallback to first + last
            first = data.get("first_name") or ""
            last = data.get("last_name") or ""
            user.full_name = f"{first} {last}".strip()
        return user
