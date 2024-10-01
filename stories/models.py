from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    meta_description = models.TextField(blank=True, null=True)  # Yeni alan
    meta_keywords = models.TextField(blank=True,)

    def generate_seo_content(self):
        """Yapay zeka kullanarak SEO açıklaması ve anahtar kelimeler oluşturur."""
        prompt_description = f"Generate an SEO-friendly meta description for the category '{self.name}' with the following description: '{self.description}'. Ensure it is under 160 characters."
        prompt_keywords = f"Generate a list of SEO-friendly keywords for the category '{self.name}'. Separate them with commas."

        try:
            # Meta Description Üretimi
            response_description = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir SEO uzmanısın ve meta açıklamaları oluşturuyorsun."},
                    {"role": "user", "content": prompt_description}
                ],
                max_tokens=60,
                temperature=0.7,
            )
            meta_description = response_description['choices'][0]['message']['content'].strip()
            meta_description = clean_text(meta_description)[:160]  # 160 karakterle sınırlama

            # Anahtar Kelimeler Üretimi
            response_keywords = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "Sen bir SEO uzmanısın ve anahtar kelimeler oluşturuyorsun."},
                    {"role": "user", "content": prompt_keywords}
                ],
                max_tokens=60,
                temperature=0.7,
            )
            keywords = response_keywords['choices'][0]['message']['content'].strip()
            keywords = clean_text(keywords)[:255]  # 255 karakterle sınırlama

            self.seo_description = meta_description
            self.seo_keywords = keywords

        except Exception as e:
            # Hata durumunda varsayılan değerler
            self.seo_description = "Bu kategori, çeşitli konularda içerikler sunmaktadır."
            self.seo_keywords = "kategori, içerik, örnek"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.seo_description or not self.seo_keywords:
            self.generate_seo_content()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Story(models.Model):
    title = models.CharField(max_length=200, blank=True, null=False)
    content = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='story_covers/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    audio_file = models.FileField(upload_to='story_audio/', blank=True, null=True)  # Ses dosyası için alan
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    meta_description = models.TextField(blank=True, help_text="SEO için meta description")
    keywords = models.CharField(max_length=255, blank=True, help_text="SEO anahtar kelimeleri")

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Story.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def __str__(self):
        return self.message
def get_notifications(request):
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    else:
        unread_notifications_count = 0
        notifications = []
    
    return {
        'unread_notifications_count': unread_notifications_count,
        'notifications': notifications,
    }

class Comment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author.username} - {self.story.title}"


class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Yanıt: {self.content[:30]}... ({self.author.username})"


class SEOSettings(models.Model):
    page_title = models.CharField(max_length=255, help_text="Sayfa başlığını girin (SEO için önemli).")
    meta_description = models.TextField(help_text="Meta açıklamaları (Google arama sonuçları için önemli).")
    keywords = models.CharField(max_length=255, help_text="Anahtar kelimeler (virgülle ayırarak).")
    robot_directives = models.TextField(blank=True, help_text="robots.txt ayarları.")

    def __str__(self):
        return self.page_title


class Backlink(models.Model):
    target_url = models.URLField(max_length=500)
    anchor_text = models.CharField(max_length=255)
    quality_score = models.IntegerField(default=0)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.target_url


class UserStory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    read_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.story.title}"

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)  # Eklenen alan

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

def home(request):
    # Tüm bildirimleri listele
    latest_notification = Notification.objects.order_by('-created_at').first()

    return render(request, 'index.html', {
        'latest_notification': latest_notification,  # En son kazanan rozet bildirimi
    })