from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Product
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Product, Cart, CartItem, UserProfile, UserLibrary, Transaction, Wishlist, Review, StoreBanner, CATEGORY_CHOICES
from django.db.models import Q


def product_list(request):
    query = request.GET.get('q')
    products = Product.objects.all()

    if query:

        search_category_code = None
        for code, name in CATEGORY_CHOICES:
            if query.lower() in name.lower():
                search_category_code = code
                break

        products = products.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(category=search_category_code)
        )

    banner = StoreBanner.objects.filter(is_active=True).first()
    featured_game = Product.objects.filter(is_featured=True).first()

    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            for item in cart.cartitem_set.all():
                cart_count += item.quantity

    return render(request, 'store/product_list.html', {
        'products': products,
        'query': query,
        'cart_count': cart_count,
        'banner': banner,
        'featured_game': featured_game,
        'categories': CATEGORY_CHOICES
    })

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('store:product-list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'store/register.html', {'form': form})

def login_user(request):
    if request.user.is_authenticated:
        return redirect('store:product-list')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('store:product-list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request,'store/Login.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('store:product-list')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    library, created = UserLibrary.objects.get_or_create(user=request.user)
    if library.products.filter(id=product_id).exists():
        messages.warning(request, f"You already own {product.name}. It is in your Repository.")
        return redirect('store:product-list')

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        messages.info(request, "This game is already in your cart!")
        return redirect('store:cart_detail')

    messages.success(request, f"Added {product.name} to your cart!")
    return redirect('store:product-list')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.product.price for item in cart_items)

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'profile': profile
    })

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()

    messages.success(request, "Item removed from the cart.")
    return redirect('store:cart_detail')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('store:product-list')

    total_price = sum(item.get_total_price() for item in cart_items)

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if profile.balance >= total_price:
        profile.balance -= total_price
        profile.save()

        library, created = UserLibrary.objects.get_or_create(user=request.user)

        for item in cart_items:
            library.products.add(item.product)

            Transaction.objects.create(
                user=request.user,
                product=item.product,
                price=item.product.price
            )

        cart_items.delete()

        messages.success(request, f"Thank you for purchasing! ₱{total_price} Added to your Repository.")
        return redirect('store:repository')
    else:
        needed = total_price - profile.balance
        messages.error(request, f"Insufficient funds! You need ₱{needed} more.")
        return redirect('store:cart_detail')

@login_required
def view_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:10]

    if request.method == 'POST' and request.FILES.get('avatar'):
        profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, "Avatar updated successfully!")
        return redirect('store:view_profile')

    return render(request, 'store/profile.html', {
        'profile': profile,
        'user': request.user,
        'transactions': transactions
    })

@login_required
def top_up_wallet(request):
    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        profile.balance += amount
        profile.save()

        messages.success(request, f"Successfully added ₱{amount} to your Crib Wallet!")
        return redirect('store:view_profile')

    amounts = [200, 400, 1000, 2000, 4000]
    return render(request, 'store/topup.html', {'amounts': amounts})

@login_required
def repository(request):
    library, created = UserLibrary.objects.get_or_create(user=request.user)
    games = library.products.all()
    return render(request, 'store/repository.html', {'games': games})

@login_required
def refund_game(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    profile = UserProfile.objects.get(user=request.user)
    profile.balance += transaction.price
    profile.save()

    library = UserLibrary.objects.get(user=request.user)
    library.products.remove(transaction.product)

    game_name = transaction.product.name
    transaction.delete()

    messages.success(request, f"Successfully refunded {game_name}. ₱{transaction.price} has been returned to your wallet.")
    return redirect('store:view_profile')

@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all()
    return render(request, 'store/wishlist.html', {'products': products})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    wishlist.products.add(product)
    messages.success(request, f"Added {product.name} to your Wishlist!")
    return redirect('store:product-list')

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.get(user=request.user)

    wishlist.products.remove(product)
    messages.success(request, "Removed from Wishlist.")
    return redirect('store:wishlist_view')


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    user_owns = False
    if request.user.is_authenticated:
        library, created = UserLibrary.objects.get_or_create(user=request.user)
        if library.products.filter(id=product.id).exists():
            user_owns = True

    if request.method == "POST" and request.user.is_authenticated:
        if not user_owns:
            messages.error(request, "You must own the game to review it!")
            return redirect('store:product_detail', product_id=product.id)

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Review posted!")
        return redirect('store:product_detail', product_id=product.id)

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'user_owns': user_owns
    })