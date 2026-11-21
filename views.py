from datetime import timedelta
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Product, Sale, Supplier


def dashboard(request):
products = Product.objects.select_related("supplier").order_by("name")
low_stock_products = [p for p in products if p.is_low_stock]
today = timezone.localdate()
today_sales = Sale.objects.filter(sold_at__date=today).aggrega

te(
total=Sum("total_amount"), units=Sum("quantity_sold")
)
context = {
"total_products": products.count(),
"low_stock_products": low_stock_products,
"today_revenue": today_sales["total"] or Decimal("0.00"),
"today_units": today_sales["units"] or 0,
"recent_sales": Sale.objects.select_related("product").order_by("-sold_at")[:8],
}
return render(request, "sales_app/dashboard.html", context)


def product_list(request):
query = request.GET.get("q", "").strip()

products = Product.objects.select_related("supplier").order_by("name")
if query:
products = products.filter(name__icontains=query)
return render(request, "sales_app/product_list.html", {"products": products, "query": query})


def product_create_or_edit(request, pk=None):
product = get_object_or_404(Product, pk=pk) if pk else None
suppliers = Supplier.objects.order_by("name")
if request.method == "POST":
name = request.POST.get("name", "").strip()
category = request.POST.get("category", "CONVENIENCE")
supplier_id = request.POST.get("supplier") or 

None
price = Decimal(request.POST.get("price", "0.00"))
quantity = int(request.POST.get("quantity", "0"))
reorder_level = int(request.POST.get("reorder_level", "10"))

if not name:
messages.error(request, "Product name is required.")
else:
if product is None:
product = Product()
product.name = name
product.category = category
product.supplier_id = supplier_id
product.price = price
product.quantity = quantity
product.reorder_level = reorder_level
product.save()
messages.success(request, f"Saved product 

'{product.name}'.")
return redirect("product_list")

return render(
request,
"sales_app/product_form.html",
{"product": product, "suppliers": suppliers, "categories": Product.CATEGORY_CHOICES},
)


def product_delete(request, pk):
product = get_object_or_404(Product, pk=pk)
if request.method == "POST":
product.delete()
messages.success(request, f"Deleted product '{product.name}'.")
return redirect("product_list")

def supplier_list(request):
if request.method == "POST":
name = request.POST.get("name", "").strip()
contact_person = request.POST.get("contact_person", "").strip()
phone = request.POST.get("phone", "").strip()
email = request.POST.get("email", "").strip()
if name:
Supplier.objects.create(
name=name, contact_person=contact_person, phone=phone, email=email
)
messages.success(request, f"Added supplier '{name}'.")
else:
messages.error(request, "Supplier name is required.")
return redirect("supplier_list")

suppliers = 

Supplier.objects.prefetch_related("products").order_by("name")
return render(request, "sales_app/supplier_list.html", {"suppliers": suppliers})


def record_sale(request):
products = Product.objects.filter(quantity__gt=0).order_by("name")
if request.method == "POST":
product_id = request.POST.get("product")
quantity_sold = int(request.POST.get("quantity_sold", "0"))
product = get_object_or_404(Product, pk=product_id)
try:
sale = Sale(product=product, quantity_sold=quantity_sold)
sale.full_clean()

sale.save()
messages.success(
request,
f"Recorded sale of {quantity_sold} x {product.name} (Total: R{sale.total_amount:.2f}).",
)
return redirect("dashboard")
except ValidationError as exc:
messages.error(request, "; ".join(exc.messages))

return render(request, "sales_app/record_sale.html", {"products": products})


def sales_report(request):
now = timezone.now()
today = timezone.localdate()
week_start = now - timedelta(days=7)

daily_sales = Sale.objects.filter(sold_at__date=today).select_related("product")
weekly_sales = Sale.objects.filter(sold_at__gte=week_start).select_related("product")

daily_total = daily_sales.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
weekly_total = weekly_sales.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")

context = {
"daily_sales": daily_sales.order_by("-sold_at"),
"weekly_sales": weekly_sales.order_by("-sold_at"),
"daily_total": daily_total,
"weekly_total": weekly_total,

}
return render(request, "sales_app/sales_report.html", context)
