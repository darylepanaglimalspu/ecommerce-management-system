from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Product
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Product, Cart, CartItem, UserProfile, UserLibrary
from django.contrib.auth.decorators import login_required

def product_list(request):
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            for item in cart.cartitem_set.all():
                cart_count += item.quantity

    return render(request, 'store/product_list.html', {
        'products': products,
        'query': query,
        'cart_count': cart_count
    })

def register_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('store:product-list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'store/register.html', {'form': form})

def login_user(request):
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

    return render(request, 'store/profile.html', {
        'profile': profile,
        'user': request.user
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