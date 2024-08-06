from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import HttpResponseServerError
from home.models import Address
from django.contrib.auth import logout
from django.contrib import messages
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
import razorpay
from django.db.models import Q
import os
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from home.models import Cartitem, Cart, Order, OrderItem, OrderAddress
from adm.models import (
    AdmProducts,
    AdmCategories,
    ProductVariant,
    ProductColor,
    ProductSize,
    Coupon,
)

# Create your views here.


def home(request):
    if request.user.is_anonymous:
        return render(request, "user/home.html")
    elif request.user.is_superuser:
        logout(request)
        return render(request, "user/home.html")
    else:
        return render(request, "user/home.html")


def useraddress(request):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user = request.user
    address = Address.objects.filter(user=user)
    return render(request, "user/useraddress.html", {"addresses": address})


def add_address(request):
    if not request.user.is_authenticated:
        return redirect("user_login")

    if request.method == "POST":
        housename_companyname = request.POST.get("Housename_companyname")
        post_office = request.POST.get("Post_office")
        street = request.POST.get("Street")
        city = request.POST.get("City")
        state = request.POST.get("State")
        country = request.POST.get("Country")
        pin_code = request.POST.get("Pin_code")

        address = Address(
            user=request.user,
            name=housename_companyname,
            postoffice=post_office,
            street=street,
            city=city,
            state=state,
            country=country,
            pin_code=pin_code,
        )
        address.save()

        return redirect("useraddress")

    return render(request, "user/add_address.html")


def edit_address(request, id):
    if not request.user.is_authenticated:
        return redirect("user_login")

    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":
        housename_companyname = request.POST.get("Edited_Housename_companyname")
        post_office = request.POST.get("Edited_Post_office")
        street = request.POST.get("Edited_Street")
        city = request.POST.get("Edited_City")
        state = request.POST.get("Edited_State")
        country = request.POST.get("Edited_Country")
        pin_code = request.POST.get("Edited_Pin_code")

        address.name = housename_companyname
        address.postoffice = post_office
        address.street = street
        address.city = city
        address.state = state
        address.country = country
        address.pin_code = pin_code
        address.save()

        return redirect("useraddress")

    return render(request, "user/edit_address.html", {"address": address})


def delete_address(request, id):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return redirect("useraddress")


def total_products(request):
    Adm_products = AdmProducts.objects.filter(is_active=True)
    products = []
    for prod in Adm_products:
        variant = ProductVariant.objects.filter(product=prod, is_active=True).first()
        if variant:
            products.append(variant)

    category = AdmCategories.objects.filter(is_active=True)
    colors = ProductColor.objects.filter(is_active=True)
    sizes = ProductSize.objects.filter(is_active=True)
    
    selected_sizes = []
    selected_colors = []
    selected_category = []

    if request.method == "POST":
        name_search = request.POST.get("name_search")
        sort_order = request.POST.get("sort", "")

        if name_search:
            products = ProductVariant.objects.filter(
                product__name__icontains=name_search
            )

        if sort_order == "Low to High":
            products = sorted(products, key=lambda x: x.price)

        elif sort_order == "High to Low":
            products = sorted(products, key=lambda x: x.price, reverse=True)

    else:
        selected_sizes = request.GET.getlist("size",) 
        selected_colors = request.GET.getlist("color",) 
        selected_category = request.GET.getlist("category",) 

    if products:
        if selected_sizes:
            products = ProductVariant.objects.filter(size__name__in=selected_sizes)

        if selected_colors:
            products = ProductVariant.objects.filter(color__name__in=selected_colors)
            print(products, "colors")

        if selected_category:
            products = ProductVariant.objects.filter(product__category__name__in=selected_category)

    return render(
        request,
        "user/total_products.html",
        {
            "products": products,
            "colors": colors,
            "sizes": sizes,
            "category": category,
            "selected_sizes": selected_sizes,
            "selected_colors": selected_colors,
            "selected_category": selected_category,
        },
    )


def roadbikes(request):
    category = AdmCategories.objects.get(name="Road Bikes", is_active=True)
    products = AdmProducts.objects.filter(category=category, is_active=True)
    return render(request, "user/roadbikes.html", {"products": products})


def gravelbikes(request):
    category = AdmCategories.objects.get(name="Gravel Bikes", is_active=True)
    products = AdmProducts.objects.filter(category=category, is_active=True)
    return render(request, "user/gravelbikes.html", {"products": products})


def mountainbikes(request):
    category = AdmCategories.objects.get(name="Mountain Bikes", is_active=True)
    products = AdmProducts.objects.filter(category=category, is_active=True)
    return render(request, "user/mountainbikes.html", {"products": products})


def product_description(request, id):
    var = ProductVariant.objects.get(id=id)
    variants = ProductVariant.objects.filter(product=var.product, is_active=True)

    colors = variants.values_list("color", flat=True).distinct()
    sizes = variants.values_list("size", flat=True).distinct()

    available_colors = ProductColor.objects.filter(id__in=colors, is_active=True)
    available_sizes = ProductSize.objects.filter(id__in=sizes, is_active=True)

    selected_color_id = request.GET.get("selected_color")
    selected_size_id = request.GET.get("selected_size")

    if selected_color_id:
        variants = variants.filter(color_id=selected_color_id)

    if selected_size_id:
        variants = variants.filter(size_id=selected_size_id)

    # Create a list of dictionaries containing variant data, including color image URLs
    variants_data = []
    for variant in variants:
        color_images = variant.images.all()  # Get all associated VariantImage objects
        color_image_urls = [
            image.image.url for image in color_images
        ]  # Get URLs for each image
        color = ProductColor.objects.get(id=variant.color_id)
        color_name = color.name
        size = ProductSize.objects.get(id=variant.size_id)
        size_name = size.name
        variants_data.append(
            {
                "id": variant.id,
                "color_id": variant.color_id,
                "size_id": variant.size_id,
                "size_name": size_name,
                "color_name": color_name,
                "price": str(variant.price),
                "offer_price": str(variant.offer_price),
                "discount": str(variant.discount),
                "stock": variant.stock,
                "is_available": variant.is_available,
                "is_active": variant.is_active,
                "color_image_urls": color_image_urls,  # Add the list of color image URLs
            }
        )

    # Create a dictionary with the data you want to send back
    response_data = {
        "products": {
            "name": var.product.name,
            # Add other product details here
        },
        "variants": variants_data,  # Use the list of dictionaries
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        # If it's an AJAX request, return JSON response
        return JsonResponse(response_data)

    # If it's not an AJAX request, render the HTML template
    return render(
        request,
        "user/product_description.html",
        {
            "products": var,
            "variants": variants,
            "colors": available_colors,
            "sizes": available_sizes,
        },
    )


def add_to_cart(request, id):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user = request.user

    try:
        product_variant = ProductVariant.objects.get(id=id)

        if product_variant.stock > 0:
            cart, created = Cart.objects.get_or_create(user=user)

            try:
                item = Cartitem.objects.get(cart=cart, product=product_variant)
                item.quantity += 1
                item.save()
                messages.success(
                    request, f"{product_variant.product} quantity updated in your cart."
                )
            except Cartitem.DoesNotExist:
                item = Cartitem(cart=cart, product=product_variant)
                item.save()
                messages.success(
                    request, f"{product_variant.product} added to your cart."
                )
        else:
            messages.error(request, f"{product_variant.product} is out of stock.")
    except ProductVariant.DoesNotExist:
        messages.error(request, f"Product variant not available.")

    return redirect("cart")


def cart(request):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user = request.user
    cart = get_object_or_404(Cart, user=user)
    cart_items = Cartitem.objects.filter(cart=cart)
    cart_coupon = cart.coupon

    total_price = 0
    for item in cart_items:
        item.offer_price = item.product.offer_price
        item.total_price_each = item.offer_price * item.quantity
        total_price += item.total_price_each

    if cart_coupon and total_price < cart_coupon.minimum_amount:
        cart_coupon = None
        cart.save()
        messages.warning(request, "Total price less than Coupon minimum amount")

    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            if not cart_coupon and total_price >= coupon.minimum_amount:
                cart.coupon = coupon
                cart.save()
                messages.success(request, "Coupon added successfully")
                return redirect("cart")
            elif cart_coupon:
                messages.warning(request, "You have already used a coupon")
            else:
                messages.warning(
                    request, "Not eligible for the current price, add more items"
                )
        except Coupon.DoesNotExist:
            messages.warning(request, "Please enter a valid coupon")

    coupon_discount = cart_coupon.discount if cart_coupon else 0
    final_total = total_price - coupon_discount
    cart.total_price = total_price
    cart.save()

    context = {
        "cart_items": cart_items,
        "total_price": total_price,
        "coupon_discount": coupon_discount,
        "final_total": final_total,
        "cart_coupon": cart_coupon,
    }

    return render(request, "user/cart.html", context)


def coupons_details(request):
    coupons = Coupon.objects.all()

    context = {
        "coupons": coupons,
    }
    return render(request, "user/coupons_details.html", context)


def remove_coupon(request):
    user = request.user

    try:
        cart = get_object_or_404(Cart, user=user)
        if cart.coupon:
            cart.coupon = None
            cart.save()
            messages.success(request, "Coupon removed successfully")
        else:
            messages.warning(request, "No coupon applied to your cart")
    except:
        messages.warning(request, "Error: Could not remove coupon")

    return redirect("cart")


def update_cart_item(request, id):
    item = get_object_or_404(Cartitem, pk=id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "increase":
            if item.quantity < item.product.stock:
                item.quantity += 1
            else:
                messages.warning(request, "Out of stock")

        elif action == "decrease":
            item.quantity = max(item.quantity - 1, 1)

        item.save()

    return redirect("cart")


def clear_cart_item(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    Cartitem.objects.filter(cart=cart).delete()
    messages.success(request, "Your cart has been cleared.")
    return redirect("cart")


def delete_cart_item(request, id):
    user = request.user
    cart = Cart.objects.get(user=user)

    try:
        item = Cartitem.objects.get(cart=cart, id=id)
        item.delete()
        messages.success(request, f"{item.product} has been removed from your cart.")
    except Cartitem.DoesNotExist:
        messages.error(request, "Cart item not found.")

    return redirect("cart")


def checkout(request):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user = request.user
    addresses = OrderAddress.objects.filter(user=user)

    selected_address_id = None
    default_address = addresses.order_by("-id").first()

    if request.method == "POST":
        selected_address_id = request.POST.get("selected_address")

        return redirect(
            "payment",
            address_id=selected_address_id,
        )
    else:
        return render(
            request,
            "user/checkout.html",
            {
                "addresses": addresses,
                "default_address": default_address,
            },
        )


def edit_checkout_address(request, id):
    if not request.user.is_authenticated:
        return redirect("user_login")

    address = get_object_or_404(OrderAddress, id=id, user=request.user)

    if request.method == "POST":
        housename_companyname = request.POST.get("Edited_Housename_companyname")
        post_office = request.POST.get("Edited_Post_office")
        street = request.POST.get("Edited_Street")
        city = request.POST.get("Edited_City")
        state = request.POST.get("Edited_State")
        country = request.POST.get("Edited_Country")
        pin_code = request.POST.get("Edited_Pin_code")

        address.name = housename_companyname
        address.postoffice = post_office
        address.street = street
        address.city = city
        address.state = state
        address.country = country
        address.pin_code = pin_code
        address.save()

        return redirect("checkout")

    return render(request, "user/edit_checkout_address.html", {"address": address})


def delete_checkout_address(request, id):
    address = get_object_or_404(OrderAddress, id=id)
    address.delete()
    return redirect("checkout")


def payment(request, address_id):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user = request.user
    address = OrderAddress.objects.get(id=address_id)
    address_id = address.id

    cart = Cart.objects.get(user=user)
    cart_items = Cartitem.objects.filter(cart=cart)
    total_price = cart.total_price
    coupon_discount = cart.coupon.discount if cart.coupon else 0
    cart_total = total_price - coupon_discount

    final_total = cart_total + 50

    total_price_tax = (final_total + (Decimal("0.02") * final_total)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )

    if request.method == "GET":
        razorpay_client = razorpay.Client(
            auth=(
                os.environ.get("RAZORPAY_KEY_ID"),
                os.environ.get("RAZORPAY_KEY_SECRET"),
            )
        )

        order_data = {
            "amount": int(total_price_tax * 100),  # Amount in paise
            "currency": "INR",
            "payment_capture": 1,  # Auto-capture the payment
        }

        try:
            payment = razorpay_client.order.create(data=order_data)
        except Exception as e:
            print(f"Razorpay API error: {str(e)}")

        context = {
            "address_id": address_id,
            "total_price": cart_total,
            "total_price_tax": total_price_tax,
        }
        return render(request, "user/payment.html", context)

    elif request.method == "POST":
        if "cash_on_delivery" in request.POST:
            payment_method_id_1 = request.POST.get("cash_on_delivery")

            if address and payment_method_id_1:
                payment_method = "Cash On Delivery"

                order = Order.objects.create(
                    user=user,
                    address=address,
                    payment_method=payment_method,
                    order_date=timezone.now(),
                    total_price=total_price,
                    coupon_discount=coupon_discount,
                    total_price_tax=total_price_tax,
                )

                for item in cart_items:
                    product = item.product
                    quantity = item.quantity
                    product_variant = product

                    if product_variant.stock >= quantity:
                        product_variant.stock -= quantity
                        product_variant.save()

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                        )
                    else:
                        print("Insufficient stock...")
                        pass

                cart.coupon = None
                cart.total_price = 0
                cart.save()

                cart_items.delete()

                return redirect(
                    "order_summary",
                    address_id=address_id,
                    order_id=order.id,
                )

        elif "razorpay" in request.POST:
            context = {
                "address_id": address_id,
                "total_price": cart_total,
                "total_price_tax": total_price_tax,
            }
            return render(request, "user/payment.html", context)


def razor(request, address_id, total_price_tax):
    try:
        user = request.user
        address = OrderAddress.objects.get(id=address_id)
        cart = Cart.objects.get(user=user)
        cart_items = Cartitem.objects.filter(cart=cart)
        total_price = cart.total_price
        coupon_discount = cart.coupon.discount if cart.coupon else 0
        cart_total = total_price - coupon_discount

        final_total = cart_total + 50

        total_price_tax = (final_total + (Decimal("0.02") * final_total)).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )

        if address:
            order = Order.objects.create(
                user=user,
                address=address,
                payment_method="Razor Pay",
                order_date=timezone.now(),
                total_price=total_price,
                coupon_discount=coupon_discount,
                total_price_tax=total_price_tax,
            )

            for item in cart_items:
                product = item.product
                quantity = item.quantity
                product_variant = product

                if product_variant.stock >= quantity:
                    product_variant.stock -= quantity
                    product_variant.save()

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                    )
                else:
                    print("Insufficient stock...")
                    pass

            cart.coupon = None
            cart.total_price = 0
            cart.save()

            cart_items.delete()

            return redirect(
                "order_summary",
                address_id=address.id,
                order_id=order.id,
            )
        else:
            pass
    except OrderAddress.DoesNotExist:
        print("Address DoesNotExist...")
        pass
    except Cart.DoesNotExist:
        print("Cart DoesNotExist...")
        pass


def order_summary(request, address_id, order_id):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user = request.user
    address = OrderAddress.objects.get(id=address_id)
    username = user.username

    orders = Order.objects.get(id=order_id, address=address)
    order_items = OrderItem.objects.filter(order=orders)
    order_total_price = orders.total_price
    coupon_discount = orders.coupon_discount if orders.coupon_discount else 0
    total_price = order_total_price - coupon_discount
    final_total = total_price + 50

    for item in order_items:
        item.offer_price = item.product.offer_price
        item.total_price_each = item.offer_price * item.quantity

    total_price_tax = (final_total + (Decimal("0.02") * final_total)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )

    context = {
        "address": address,
        "username": username,
        "orders": orders,
        "order_items": order_items,
        "order_total_price": order_total_price,
        "discount": coupon_discount,
        "total_price_tax": total_price_tax,
    }

    return render(request, "user/order_summary.html", context)


def my_orders(request):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user = request.user
    orders = Order.objects.filter(user=user)
    order_items = OrderItem.objects.filter(order__in=orders).order_by("-id")

    return render(
        request, "user/my_orders.html", {"order_items": order_items, "orders": orders}
    )


def cancel_order(request, order_id, product_id):
    order = get_object_or_404(Order, id=order_id)
    order_item = get_object_or_404(OrderItem, order=order, product_id=product_id)

    if order_item:
        order_item.order_status = "Cancelled"
        order_item.save()

    source = request.GET.get("source")

    if source == "my_orders":
        return redirect("my_orders")
    elif source == "single_order":
        return redirect("single_order", order_id=order_id)
    else:
        return redirect("home")


def single_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_item = OrderItem.objects.filter(order=order)

    return render(
        request, "user/single_order.html", {"order": order, "order_item": order_item}
    )


def return_order(request, order_id, product_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        order_item = get_object_or_404(OrderItem, order=order, product_id=product_id)
        return_reason = request.POST.get("return_reason")

        if order_item:
            order_item.order_status = "Return Requested"
            order_item.return_reason = return_reason
            order_item.save()

    return redirect("my_orders")


def invoice(request, address_id, order_id):
    if not request.user.is_authenticated:
        return redirect("user_login")

    user = request.user
    address = OrderAddress.objects.get(id=address_id)
    username = user.username

    orders = Order.objects.get(id=order_id, address=address)
    order_items = OrderItem.objects.filter(order=orders)
    order_total_price = orders.total_price
    coupon_discount = orders.coupon_discount if orders.coupon_discount else 0
    total_price = order_total_price - coupon_discount
    final_total = total_price + 50

    for item in order_items:
        item.offer_price = item.product.offer_price
        item.total_price_each = item.offer_price * item.quantity

    total_price_tax = (final_total + (Decimal("0.02") * final_total)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )

    context = {
        "address": address,
        "username": username,
        "orders": orders,
        "order_items": order_items,
        "order_total_price": order_total_price,
        "discount": coupon_discount,
        "total_price_tax": total_price_tax,
    }

    return render(request, "user/invoice.html", context)


def search(request):
    if request.method == "GET":
        query = request.GET.get("query")

        if query:
            product = ProductVariant.objects.filter(
                Q(price__icontains=query, is_active=True)
                | Q(offer_price__icontains=query, is_active=True)
                | Q(product__name__icontains=query, is_active=True)
                | Q(color__name__icontains=query, is_active=True)
                | Q(product__category__name__icontains=query, is_active=True)
                | Q(
                    size__name__icontains=query, is_active=True
                )  # Add the condition for is_active=True
            )

            return render(request, "user/search.html", {"products": product})
        else:
            product = ProductVariant.objects.none()
            return render(request, "user/search.html", {"products": product})
    else:
        # Handle other HTTP methods if necessary
        return HttpResponse("Method not allowed", status=405)


def wallet(request):
    print(request, "oooooo")
    try:
        user = request.user
        orders = Order.objects.filter(user=user, payment_method="Razor Pay")
        order_ids = orders.values_list("id", flat=True)
        order_items = OrderItem.objects.filter(
            Q(order_id__in=order_ids)
            & (Q(order_status="Return Requested") | Q(order_status="Cancelled"))
        )

        total_refund_amount = 0

        for item in order_items:
            if not item.refund_added_to_wallet:
                total_refund_amount += item.order.total_price_tax  # Updated here
                item.refund_added_to_wallet = True
                item.save()  # Save the item

        user.wallet_balance += Decimal(total_refund_amount)
        user.save()
        return render(
            request,
            "user/wallet.html",
            {"order_items": order_items, "total_refund_amount": total_refund_amount},
        )

    except Exception as e:
        error_message = "An error occurred: {}".format(str(e))
        return HttpResponseServerError(error_message)

