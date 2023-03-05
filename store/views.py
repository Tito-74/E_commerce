import datetime
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Products, Order, OrderItems, ShippingAddress
from . utils import  cartData, guestOrders
# cookieCart,
# Create your views here.

def store(request, *args, **kwargs):
  data = cartData(request)
  cartItems = data['cartItems']

  products = Products.objects.all()
  context = {"products": products, "cartItems":cartItems}
  return render(request, 'store/store.html', context)

def cart(request, *args, **kwargs):
    print("cartss is executed")
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    print("cartss:", cartItems)
    print("cartss:", items)

  
    context = {"items":items,  "order": order, "cartItems":cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request, *args, **kwargs):
  data = cartData(request)
  # cookieData = cookieCart(request)
  cartItems = data['cartItems']
  order = data['order']
  items = data['items']
 
  context = {"items":items,  "order": order, "cartItems":cartItems}
  return render(request, 'store/checkout.html', context)


def updateItem(request):
  data = json.loads(request.body)
  productId = data['productId']
  print('data:', data)
  action = data['action']
  print('productId:', productId)
  print('action:', action)
  customer = request.user.customer 
  print('customer:', customer)
  product = Products.objects.get(id=productId) 
  order, created = Order.objects.get_or_create(customer=customer, completed =False)

  orderItem, created = OrderItems.objects.get_or_create(order = order, product=product)
  if action == 'add':
    print('orderItem quantity:', orderItem.quantity)
    orderItem.quantity = (orderItem.quantity + 1)
    print('orderItem quantity plus:', orderItem.quantity)
  elif action == 'remove':
    print('orderItem quantity remove:', orderItem.quantity)
    orderItem.quantity = (orderItem.quantity - 1)
    print('orderItem quantity remove:', orderItem.quantity)

  orderItem.save()
  if orderItem.quantity <= 0:
    orderItem.delete()

  return JsonResponse("item was add", safe=False)

@csrf_exempt
def processOrder(request):
    # print("datas", request.body)
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
      customer = request.user.customer
      order, created = Order.objects.get_or_create(customer=customer, completed=False)
    else:
      customer, order = guestOrders(request, data)

    total = float(data['form']['total'])
    order.Transaction_id = transaction_id
    print(type(total))
    print(type(order.get_cart_total))
    if total == float(order.get_cart_total):
      print("not equals:", "total:",total, "orders:",order.get_cart_total)
      order.completed = True
    order.save()
  
      
      

    if order.shipping == True:
        ShippingAddress.objects.create(
          customer=customer,
          order=order,
          address=data['shipping']['address'],
          city=data['shipping']['city'],
          state=data['shipping']['state'],
          zipcode=data['shipping']['zipcode'],
        )
    return JsonResponse("payment has been made", safe=False)