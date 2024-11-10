from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
import os
from django.conf import settings
import pandas as pd
from egroceryapp.forms import LoginForm, AddToCartForm, ProfileRegisterForm, UserRegisterForm
from egroceryapp.models import *
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from django.db.models import Q
from django.urls import reverse
import random
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
import razorpay
from django.views.decorators.http import require_POST
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db import transaction

csv_file_path = os.path.join(
    settings.STATIC_ROOT, "csv", "ECommerce_consumer_behaviour.csv"
)
csv_file_path1 = os.path.join(settings.STATIC_ROOT, "csv", "nwfilevsc.csv")
rules = os.path.join(settings.STATIC_ROOT, "csv", "association_rules.csv")
data = pd.read_csv(rules, encoding="utf-8")
product_data = pd.read_csv(csv_file_path1, encoding="utf-8")
product_data_ecommerce_csv = pd.read_csv(csv_file_path, encoding="utf-8")
data_cleaned = product_data.dropna()


def index(request):
    
    ecommerce_csv_department = product_data_ecommerce_csv["department"].unique()
    unique_categories = set(ecommerce_csv_department)

    data_to_display = data_cleaned.sample(n=20)
    cart_dtl_data = get_cart_details(request.user)
    total_price = cart_total_price(request.user)
    print(data_to_display)

    return render(
        request,
        "index.html",
        {
           
            "unique_categories": unique_categories,
            "csv_data": data_to_display,
            "cart_dtl_data": cart_dtl_data,
            "total_price": total_price,
        },
    )


# Function to get recommendations for a given product
def get_recommendations(product):
    # Set confidence and lift thresholds

    min_confidence = 0.5
    min_lift = 1
    # Filter rules based on thresholds
    filtered_rules = data[
        (data["confidence"] > min_confidence) & (data["lift"] > min_lift)
    ]
    # Filter rules based on the given product
    product_rules = filtered_rules[
        filtered_rules["antecedents"].apply(lambda x: product in x)
    ]

    # Display the recommendations
    recommendations = list(set(product_rules["consequents"].explode().tolist()))

    return recommendations


def search_results(request):
    query = request.GET.get("query", "")

    # Get recommended values
    recommendations = get_recommendations(query)

    # Convert frozenset objects to strings
    recommended_values = set(recommendations)
    lists = [
        ast.literal_eval(s.replace("frozenset(", "[").replace(")", "]"))
        for s in recommendations
    ]
    flattened_list = [item for sublist in lists for item in sublist]
    final_list = [list(item) for item in flattened_list]
    flattened_list1 = [item for sublist in final_list for item in sublist]
    matching_products = data_cleaned[
        data_cleaned["Product_Category"].isin(flattened_list1)
    ]
    matching_products_random = matching_products.sample(frac=1).reset_index(drop=True)

    # Get similar products using KNN
    similar_products = get_similar_products(query, knn_model, vectorizer)

    context = {
        "query": query,
        "recommendations": recommended_values,
        "matching_products_random": matching_products_random,
        "similar_products": similar_products,
    }
    return render(request, "search_results.html", context)


# Assuming data_cleaned is your DataFrame containing product data
product_data = data_cleaned["Product_Name"].astype(str)

# Step 1: Vectorize Product Data
vectorizer = TfidfVectorizer()
product_vectors = vectorizer.fit_transform(product_data)

# Step 2: Train KNN Model
knn_model = NearestNeighbors(n_neighbors=24, metric="cosine")
knn_model.fit(product_vectors)


def get_similar_products(query, knn_model, vectorizer):
    # Step 3: Vectorize Query
    query_vector = vectorizer.transform([query])

    # Step 4: Query Similar Products
    _, indices = knn_model.kneighbors(query_vector)

    # Step 5: Display Results
    similar_products = data_cleaned.iloc[indices[0]]
    return similar_products


def suggestion(request):
    return render(request, "suggestion.html")


# Assuming you have already loaded and cleaned your data in the 'data_cleaned' variable
def search_suggestions(request):
    query = request.GET.get("q", "")

    # Use '|' (OR operator) to combine conditions for both columns
    suggestions = data_cleaned[
        data_cleaned["Product_Name"].str.contains(query, case=False)
        | data_cleaned["Product_Category"].str.contains(query, case=False)
    ]

    # Extract both "Product_Name" and "Product_Category" columns from the DataFrame
    suggestions = suggestions[["Product_Name", "Product_Category"]][:10].to_dict(
        orient="records"
    )

    return JsonResponse(suggestions, safe=False)


def search_suggestion_for_all(values):
    values_for_recomd = values
    all_recommendations = set()
    matching_products_random_list = []  # Initialize outside the loop

    for category in values_for_recomd:
        category_recommendations = get_recommendations(category)
        all_recommendations.update(category_recommendations)

    # Extract only frozenset values
    recommended_values = set(all_recommendations)
    lists = [
        ast.literal_eval(s.replace("frozenset(", "[").replace(")", "]"))
        for s in recommended_values
    ]
    flattened_list = [item for sublist in lists for item in sublist]
    final_list = [list(item) for item in flattened_list]
    
    # Convert each sublist to a string
    result_list = ["+".join(sublist) for sublist in final_list]
    
    # Convert the numpy array to a Python list
    flattened_list1 = (
        result_list if isinstance(result_list, list) else flattened_list.tolist()
    )
    
    matching_products_random = data_cleaned[
        data_cleaned["Product_Category"].isin(flattened_list1)
    ]
    
    matching_products_random = matching_products_random.sample(
        frac=0.5
    ).reset_index(drop=True)
    
    matching_products_random_list = matching_products_random.to_dict(
        orient="records"
    )

    return matching_products_random_list


def search_results_suggestion(request):
    query = request.GET.get("query", "")

    # Search for matching products based on both name and category
    matching_products = data_cleaned[
        (data_cleaned["Product_Name"].str.contains(query, case=False))
        | (data_cleaned["Product_Category"].str.contains(query, case=False))
    ]
    if not matching_products.empty:
        # Get the unique product categories for the matching products
        unique_categories = matching_products["Product_Category"].unique()
        # print(unique_categories)
        matching_products_random = search_suggestion_for_all(unique_categories)
        # Collect recommendations for each unique category
        # print(matching_products_random)

        # Store matching_products_random in the session
        request.session["matching_products_random"] = matching_products_random

    else:
        # If no matching products, set recommendations and matching_products_random to empty
        # recommended_values = set()
        matching_products_random = pd.DataFrame()

    # Get similar products using KNN
    similar_products = get_similar_products(query, knn_model, vectorizer)
    print(similar_products)
    context = {
        "query": query,
        "matching_products_random": matching_products_random,
        "similar_products": similar_products,
    }

    return render(request, "shop.html", context)


def shop(request):
    total_price = cart_total_price(request.user)
    data_to_display = data_cleaned.sample(n=48)
    
    return render(
        request,
        "shop.html",
        {
            "data_to_display":data_to_display,
            "total_price": total_price,
        },
    )


def single_product(request, Product_detail_id):
    product_detail = data_cleaned[data_cleaned["Product_detail_id"] == Product_detail_id]

    if product_detail.empty:
        return render(request, "product_not_found.html")

    product_name = product_detail.iloc[0]["Product_Name"]
    product_category = product_detail.iloc[0]["Product_Category"]
    product_Price = product_detail.iloc[0]["Product_Price"]
    product_Image_URL = product_detail.iloc[0]["Product_Image_URL"]
    Product_dtl_id = product_detail.iloc[0]["Product_detail_id"]
    Product_dtl_rating = product_detail.iloc[0]["rating"]
    print(Product_dtl_rating)

    similar_products = get_similar_products(product_name, knn_model, vectorizer)
    category_recommendations = get_recommendations(product_category)
    singleProduct_racommand = search_suggestion_for_all(category_recommendations)
    # print(similar_products)

    if singleProduct_racommand:
        context = {
            "product_name": product_name,
            "product_category": product_category,
            "product_Price": product_Price,
            "product_Image_URL": product_Image_URL,
            "Product_dtl_id":Product_dtl_id,
            "Product_dtl_rating":Product_dtl_rating,
            "matching_products_random": singleProduct_racommand,
        }
        return render(request, "single_product.html", context)
    
    elif not similar_products.empty:
        # print(similar_products)
        similar_products_list = similar_products.to_dict(orient="records")
        # Shuffle the list
        random.shuffle(similar_products_list)
        context = {
            "product_name": product_name,
            "product_category": product_category,
            "product_Price": product_Price,
            "product_Image_URL": product_Image_URL,
            "Product_dtl_rating":Product_dtl_rating,
            "matching_products_random": similar_products_list,
        }
        return render(request, "single_product.html", context)

    else:
        return render(request, "product_not_found.html")


def loginform(request):
    return render(request, "myaccount.html")


@login_required
def sign_out(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


def myaccount(request):
    if request.user.is_authenticated:
        total_price = cart_total_price(request.user)
        return render(request, "myaccount.html",{"total_price":total_price})  
             
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user:
                auth_login(request, user)  # Use auth_login instead of login
                messages.success(request, f"Hi {username.title()}, welcome back!")
                return redirect("index")
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()
    total_price = cart_total_price(request.user)
    return render(request, "myaccount.html", {"form": form})
    
    # return render(request, "myaccount.html", {"total_price": total_price})


def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        p_reg_form = ProfileRegisterForm(request.POST)
        if form.is_valid() and p_reg_form.is_valid():
            user = form.save()
            p_data = p_reg_form.cleaned_data  # Get profile form data

            # Create the user's profile and set the pincode, district, and state
            profile = Profile.objects.create(user=user, **p_data)

            messages.success(request, 'Your account has been sent for approval!')
            auth_login(request, user)  # Automatically log in the user
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please check your data.')

    else:
        form = UserRegisterForm()
        p_reg_form = ProfileRegisterForm()

    context = {
        'form': form,
        'p_reg_form': p_reg_form
    }
    return render(request, 'signup.html',context)


@login_required
@ensure_csrf_cookie
def add_to_cart_dbs(request, productID):
    # print(productID)
    if request.method == "POST":
        form = AddToCartForm(request.POST)
        # print(form)
        if form.is_valid():
            # Check if the item is not already in the wishlist
            productID = form.cleaned_data["productID"]
            quantity = form.cleaned_data["quantity"]
            product_price = form.cleaned_data["product_price"]
            # subtotal_price = int(product_price) * int(quantity)
            user = request.user

            if not add_To_Cart.objects.filter(
                user=user, prodcut_Id_Add=productID
            ).exists():
                add_To_Cart.objects.create(
                    user=user,
                    prodcut_Id_Add=productID,
                    quantity=quantity,
                    product_price=product_price,
                )
                return JsonResponse({"message": "Item Added Successfully."})
            else:
                return JsonResponse(
                    {"error": "Item already in Cart."}, status=400
                )
        else:
            return JsonResponse(
                {"error": "Form data is invalid.", "errors": form.errors}, status=400
            )
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)


def get_cart_details(user):
    user_id = user.id
    cart_data = add_To_Cart.objects.filter(user=user_id)
    cart_dtl_data = []
    count = 0
    for item in cart_data:
        count = count + 1
        product_id = item.prodcut_Id_Add
        subtotal_price = item.subtotal_price

        # print(subtotal_price)
        product_detail = data_cleaned[
            data_cleaned["Product_detail_id"] == int(product_id)
        ].to_dict("records")
        if product_detail:
            cart_dtl_data.extend(product_detail)

    return cart_dtl_data


# def cart_list_of_item(request):


@login_required
def cart(request):
    cart_dtl_data = get_cart_details(request.user)
    total_price = cart_total_price(request.user)
    cart_data = add_To_Cart.objects.filter(user=request.user)
    discount_data = Discount_data.objects.get(
                user=request.user
            )
    
    grand_totalPrice = discount_data.grand_total
    discounted_price = discount_data.total_price-discount_data.grand_total
    print(discounted_price)
    print(grand_totalPrice)

    context_list = []

    for value in cart_dtl_data:
        cart_id = value["Product_detail_id"]
        matching_items = cart_data.filter(prodcut_Id_Add=int(cart_id))

        for item in matching_items:
            context_list.append(
                {
                    "item": item,
                    "detail": value,
                }
            )

    context = {
        "cart_dtl_data": cart_dtl_data,
        "total_price": total_price,
        "context_list": context_list,
        "discounted_price":discounted_price,
        "grand_totalPrice":grand_totalPrice,
    }

    return render(request, "cart.html", context)


def cart_total_price(user):
    # print(user)

    total_price = 0
    if user.is_authenticated:
        cart_data = add_To_Cart.objects.filter(user=user)
        # print([ i.quantity for i in cart_data])
        for item in cart_data:
            # Access the 'Product_Price' value from each dictionary
            product_price_str = item.subtotal_price

            try:
                product_price = int(product_price_str)
            except ValueError:
                # Handle the case where the conversion fails (e.g., 'N/A' or invalid string)
                product_price = 0

            # Add the product_price to total_price
            total_price += product_price
    return total_price


# def cart_price_subtotal(user):
#     cart_dtl_data = get_cart_details(user)
#     # Initialize total_price to 0
#     user_id = user.id
#     cart_data = add_To_Cart.objects.filter(user=user_id)
#     for item in cart_data:
#         print(item)
#     print(cart_dtl_data)
#     print(cart_data)


#     return cart_data

@login_required
def initiate_payment(request):
    if request.method == "POST":
        discount_data = Discount_data.objects.get(
                user=request.user
            )
        grand_totalPrice = discount_data.grand_total
        amount = grand_totalPrice*100  
        email = request.user.email
        name = f"{request.user.first_name} {request.user.last_name}"

        print(email , name)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET)
        )

        payment_data = {
            "amount": amount,
            "currency": "INR",
            "receipt": "order_receipt",
            "notes": {
                "email": email,
            },
        }

        order = client.order.create(data=payment_data)
        print(order)
        # Include key, name, description, and image in the JSON response
        response_data = {
            "id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": settings.RAZORPAY_API_KEY,
            "name": "Pandit E-grocery",
            "description": "Payment for Your Product",
            "image": "https://yourwebsite.com/logo.png",  # Replace with your logo URL
        }

        return JsonResponse(response_data)

    return render(request, "cart.html")


def payment_success(request):
    return render(request, "payment_success.html")


def payment_failed(request):
    return render(request, "payment_failed.html")


@require_POST
@login_required
def update_cart_item(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        cart_item_id = request.POST.get("cart_item_id")
        new_quantity = request.POST.get("new_quantity")

        try:
            cart_item = add_To_Cart.objects.get(
                prodcut_Id_Add=cart_item_id, user=request.user
            )
            
            
            cart_item.quantity = new_quantity
            cart_item.save()
            
            new_subtotal = cart_item.subtotal_price
            new_total_price = cart_total_price(request.user)
            return JsonResponse(
                {
                    "success": True,
                    "new_subtotal": new_subtotal,
                    "new_total_price": new_total_price,
                }
            )
        except add_To_Cart.DoesNotExist:
            return JsonResponse({"success": False, "error": "Item not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})


# views.py
@require_POST
@login_required
def delete_cart_item(request):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        cart_item_id = request.POST.get("cart_item_id")
        # print(cart_item_id)

        try:
            cart_item = add_To_Cart.objects.get(
                prodcut_Id_Add=cart_item_id, user=request.user
            )
            cart_item.delete()
            return JsonResponse({"success": True})
        except add_To_Cart.DoesNotExist:
            return JsonResponse({"success": False, "error": "Item not found"})

    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def get_cart_data(request):
    # Assuming you have a function to get the user's cart data
    cart_dtl_data = get_cart_details(request.user)
    total_price = cart_total_price(request.user)
    cart_data = add_To_Cart.objects.filter(user=request.user)

    context_list = []

    for value in cart_dtl_data:
        cart_id = value["Product_detail_id"]
        matching_items = cart_data.filter(prodcut_Id_Add=int(cart_id))

        for item in matching_items:
            context_list.append(
                {
                    "item": {
                        "id": item.id,
                        "subtotal_price": item.subtotal_price,
                        "quantity": item.quantity,
                        # Add other fields as needed
                    },
                    "detail": {
                        "Product_Name": value[
                            "Product_Name"
                        ],  # Assuming 'Product_Name' is the key
                        # Add other fields from 'value' as needed
                    },
                }
            )

    # print(context_list)

    # Do not convert the list to a JSON string here
    # DjangoJSONEncoder will take care of serialization in JsonResponse
    context_json = context_list

    # Process context_json as needed

    return JsonResponse(
        {"cart_data": context_json, "total_price": total_price},
        encoder=DjangoJSONEncoder,
    )

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")


@login_required
def handle_successful_purchase(request):
    # Create a new order record with 'Paid' payment status
       # Create a new order record with 'Paid' payment status
    user = request.user
    new_order = Order.objects.create(user=user, payment_status='Paid')

    # Associate existing cart items with the new order
    cart_items = add_To_Cart.objects.filter(user=user)
    print(item.prodcut_Id_Add for item in cart_items)
    
    new_order.total_items_placed = cart_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
    new_order.total_price = cart_items.aggregate(Sum('subtotal_price'))['subtotal_price__sum'] or 0
    new_order.total_discounted_price = cart_items.aggregate(Sum('subtotal_price'))['subtotal_price__sum'] or 0
    new_order.grand_total = cart_items.aggregate(Sum('subtotal_price'))['subtotal_price__sum'] or 0
    new_order.products = ','.join(item.prodcut_Id_Add for item in cart_items)
    new_order.product_All_quantity = ','.join(str(item.quantity) for item in cart_items)


    new_order.save()

    # Associate existing cart items with the new order directly
    

    # Clear existing cart items
    cart_items.delete()

    # Optionally, you might want to create a new Discount_data instance for the user
    # to start fresh with discounts for the next order.
    new_discount_data = Discount_data.objects.create(user=user)
    new_discount_data.update_totals()

    # Render the purchase success page or redirect to another page
    return render(request, 'purchase_success.html')

@login_required
def order_history(request):
    user = request.user
    
    history_items = Order.objects.filter(user=user)
    order_details = []

    for order in history_items:
        if order.products:
            product_ids = [int(pid) for pid in order.products.split(',') if pid.isdigit()]
            filtered_data = data_cleaned[data_cleaned["Product_detail_id"].isin(product_ids)]
            
            product_quantitys = None
            if order.product_All_quantity:
                product_quantitys = [int(qty) for qty in order.product_All_quantity.split(',') if qty.isdigit()]
            
            order_products = []

            # Check if product_quantitys is not None before iterating
            if product_quantitys:
                # Loop through both product IDs and quantities simultaneously
                for product_id, quantity in zip(product_ids, product_quantitys):
                    product_detail = filtered_data[filtered_data["Product_detail_id"] == product_id].iloc[0]
                    order_status = order.payment_status
                    # print(order_status)
                    order_products.append({'product_detail': product_detail, 'quantity': quantity,'order_status':order_status})

            order_details.append({'order': order, 'products': order_products})


    return render(request, 'order_history.html', {'order_details': order_details})



