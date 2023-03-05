import json
from . models import *



def cookieCart(request):
      print("not logged in user")
      try:
        cart = json.loads(request.COOKIES['cart'])
        print("cart_test1:", cart)
      except:
        cart = {}
        print("cart_test:", cart)
      items = []
      order = {"get_cart_total":0, "get_cart_items":0, "shipping":False}
      cartItems = order['get_cart_items']

      for i in cart:
        try:
          print("cart_test:", cart)
          cartItems += cart[i]['quantity'] 
          product = Products.objects.get(id = i)
          total = (product.price* cart[i]['quantity'])
          order['get_cart_total'] += total
          order['get_cart_items'] += cart[i]['quantity']

          item = {
            'product':{
              'id':product.id,
              'name':product.name,
              'price':product.price,
              'imageURL':product.imageURL, 
            },
            'quantity':cart[i]['quantity'],
            'get_total':total
            }
          items.append(item)

          if product.digital == False:
            order["shipping"] = True

        except:
            pass 

      return {"items":items,  "order": order, "cartItems":cartItems}
      

def cartData(request):
  if request.user.is_authenticated:
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, completed =False)
    items = order.orderitems_set.all()
    cartItems = order.get_cart_items
  else:
    cookieData = cookieCart(request)
    print("cookieData:", cookieData)
    cartItems = cookieData['cartItems']
    order = cookieData['order']
    items = cookieData['items']
  return {"items":items,  "order": order, "cartItems":cartItems}


def guestOrders(request, data):
  #  print("user in not logged in")
      print("cookies:", request.COOKIES)
      name = data['form']['name']
      email = data['form']['email']
      cookieData = cookieCart(request)
      items = cookieData['items']
      customer, created = Customer.objects.get_or_create(name=name, email=email,)
      customer.name = name
      customer.save()
      order = Order.objects.create(customer=customer, completed = False)
      for item in items:
        product = Products.objects.get(id = item["product"]["id"])
        orderitem = OrderItems.objects.create(product=product,
                                              order = order,
                                              quantity = item["quantity"],
                                              )
      return customer, order