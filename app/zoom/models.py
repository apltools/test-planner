from django.db import models

# Create your models here.

class OAuth2Token(models.Model):
    name = models.CharField(max_length=40)
    token_type = models.CharField(max_length=40)
    access_token = models.CharField(max_length=1024)
    refresh_token = models.CharField(max_length=1024)
    expires_at = models.PositiveIntegerField()
    user = models.ForeignKey('planner.User', on_delete=models.CASCADE)

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

    def __str__(self):
        return f'{self.name}: {self.user}'

    class Meta:
        unique_together = ('name', 'user',)
        verbose_name = 'OAuth2 Token'
        verbose_name_plural = 'OAuth2 Tokens'


class ZoomMeeting(models.Model):
    meeting_id = models.PositiveIntegerField()
