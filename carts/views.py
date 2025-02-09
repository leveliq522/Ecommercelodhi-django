from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Product
from .models import Cart, CartItem

# Helper function to get or create a cart ID for the session
def _cart_id(request):
    cart = request.session.get('cart_id', None)  # Try to get the cart_id from the session
    if not cart:
        cart = request.session.session_key  # Use session_key if cart_id does not exist
        request.session['cart_id'] = cart  # Store the cart_id in the session
    return cart

# Function to add a product to the cart
def add_cart(request, product_id):
    try:
        # Fetch the product based on the product ID
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return HttpResponse("Product not found.", status=404)  # Return a 404 if the product does not exist

    # Try to get the existing cart or create a new one if it doesn't exist
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # If the cart does not exist, create a new cart object
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    # Try to get the existing cart item or create a new one
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1  # If the item exists, increase the quantity
        cart_item.save()
    except CartItem.DoesNotExist:
        # If the cart item does not exist, create a new one
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.save()

    return redirect('cart')  # Make sure you have a URL pattern named 'cart' that corresponds to the cart page

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1 :
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

# Cart view to display the cart contents
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        # Try to get the cart based on the session's cart_id
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectNotExist:
        pass

    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }



    # Pass cart items to the template to render the cart page
    return render(request, 'store/cart.html', context)
