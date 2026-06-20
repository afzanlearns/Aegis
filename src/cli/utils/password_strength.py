import re


class PasswordStrength:
    """Evaluate and validate password strength."""

    MIN_LENGTH = 12
    RECOMMENDED_LENGTH = 16

    @staticmethod
    def score(password: str) -> int:
        """Return a numeric strength score (0-100)."""
        score = 0

        if len(password) >= PasswordStrength.MIN_LENGTH:
            score += 20
        if len(password) >= PasswordStrength.RECOMMENDED_LENGTH:
            score += 10

        if re.search(r"[a-z]", password):
            score += 10
        if re.search(r"[A-Z]", password):
            score += 15
        if re.search(r"[0-9]", password):
            score += 15
        if re.search(r"[!@#$%^&*()_+\-=\[\]{}|:;<>?,./]", password):
            score += 20

        unique_chars = len(set(password))
        score += min(unique_chars, 10)

        return min(score, 100)

    @staticmethod
    def label(password: str) -> str:
        """Return a human-readable strength label."""
        s = PasswordStrength.score(password)
        if s >= 80:
            return "Very Strong"
        elif s >= 60:
            return "Strong"
        elif s >= 40:
            return "Moderate"
        elif s >= 20:
            return "Weak"
        return "Very Weak"

    @staticmethod
    def is_acceptable(password: str) -> bool:
        """Return True if the password meets minimum requirements."""
        if len(password) < PasswordStrength.MIN_LENGTH:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*()_+-=[]{}|:;<>?,./" for c in password)
        return all([has_upper, has_lower, has_digit, has_symbol])

    @staticmethod
    def suggestions(password: str) -> list[str]:
        """Return improvement suggestions."""
        suggestions = []
        if len(password) < PasswordStrength.RECOMMENDED_LENGTH:
            suggestions.append(f"Use at least {PasswordStrength.RECOMMENDED_LENGTH} characters")
        if not re.search(r"[a-z]", password):
            suggestions.append("Add lowercase letters")
        if not re.search(r"[A-Z]", password):
            suggestions.append("Add uppercase letters")
        if not re.search(r"[0-9]", password):
            suggestions.append("Add numbers")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|:;<>?,./]", password):
            suggestions.append("Add symbols")
        return suggestions
