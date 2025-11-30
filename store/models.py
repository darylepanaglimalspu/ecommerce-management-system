from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = (
    ('FPS', 'First-Person Shooter'),
    ('RPG', 'Role-Playing Game'),
    ('MOBA', 'Multiplayer Online Battle Arena'),
    ('SIM', 'Simulation'),
    ('HORROR', 'Horror'),
    ('Indie', 'Indie'),
)

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='INDIE')
    image = models.ImageField(upload_to='game_covers/', blank=True, null=True)
    is_featured = models.BooleanField(default=False,
    help_text="Check this to show this game in the big Featured section")

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet: ₱{self.balance}"

class UserLibrary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Library"

    class Meta:
        verbose_name_plural = "User Libraries"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bought {self.product.name} - {self.date}"

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} stars)"

class StoreBanner(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
        