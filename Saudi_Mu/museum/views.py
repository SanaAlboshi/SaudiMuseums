from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Authority, AuthorityType, Museum, MuseumComment, Booking
from .forms import AuthorityForm, MuseumForm
from museum.models import Bookmark


# ==========================
# إضافة هيئة
# ==========================
@login_required(login_url='account:sign_in')
def add_authority(request):
    if request.method == "POST":
        form = AuthorityForm(request.POST, request.FILES)

        if form.is_valid():
            authority = form.save(commit=False)
            authority.owner = request.user

            # تعيين نوع الهيئة تلقائي (أول نوع موجود في DB)
            default_type = AuthorityType.objects.first()
            authority.type = default_type

            authority.save()
            messages.success(request, "تم إضافة الهيئة بنجاح")
            return redirect('account:authority_profile', authority_id=authority.id)
    else:
        form = AuthorityForm()

    return render(request, "museum/add_authority.html", {"form": form})


# ==========================
# عرض جميع الهيئات
# ==========================
def all_authority(request):
    authority_type = request.GET.get("type", "")

    if authority_type:
        authorities_list = Authority.objects.filter(type_id=authority_type).order_by("id")
    else:
        authorities_list = Authority.objects.all().order_by("id")

    paginator = Paginator(authorities_list, 3)  # 3 هيئات لكل صفحة
    page_number = request.GET.get('page')
    authorities = paginator.get_page(page_number)

    types = AuthorityType.objects.all()

    return render(request, 'museum/all_authority.html', {
        "authorities": authorities,
        "types": types,
        "selected": authority_type,
        "paginator": paginator,
    })


# ==========================
# تحديث الهيئة
# ==========================
@login_required(login_url='account:sign_in')
def update_authority(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)

    if request.user != authority.owner and not request.user.is_staff:
        messages.error(request, "ليس لديك صلاحية تعديل هذه الهيئة")
        return redirect('home')

    if request.method == "POST":
        form = AuthorityForm(request.POST, request.FILES, instance=authority)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الهيئة بنجاح")
            return redirect('all_authority')
    else:
        form = AuthorityForm(instance=authority)

    return render(request, 'museum/add_authority.html', {
        "form": form,
        "update_mode": True,
    })


# ==========================
# حذف الهيئة
# ==========================
@login_required(login_url='account:sign_in')
def delete_authority(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)

    if request.user != authority.owner and not request.user.is_staff:
        messages.error(request, "ليس لديك صلاحية حذف هذه الهيئة")
        return redirect('home')

    authority.delete()
    messages.success(request, "تم حذف الهيئة بنجاح")
    return redirect('all_authority')


# ==========================
# إضافة متحف
# ==========================
@login_required(login_url='account:sign_in')
def add_museum(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)

    if request.user != authority.owner:
        return redirect('home')

    if request.method == "POST":
        form = MuseumForm(request.POST, request.FILES)
        if form.is_valid():
            museum = form.save(commit=False)
            museum.authority = authority
            museum.save()
            messages.success(request, "تمت إضافة المتحف للهيئة بنجاح")
            return redirect('add_museum', authority_id=authority_id)
    else:
        form = MuseumForm()

    return render(request, 'museum/add_museum.html', {
        "form": form,
        "authority": authority
    })


# ==========================
# تفاصيل الهيئة + تعليقات المتاحف
# ==========================
def details(request, authority_id):
    authority = get_object_or_404(Authority, id=authority_id)
    museums = Museum.objects.filter(authority=authority)

    # استقبال تعليق جديد
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("account:sign_in")

        comment_text = request.POST.get("comment")
        rating = request.POST.get("rating")
        museum_id = request.POST.get("museum_id")
        museum = get_object_or_404(Museum, id=museum_id)

        MuseumComment.objects.create(
            museum=museum,
            user=request.user,
            comment=comment_text,
            rating=rating
        )
        return redirect("details", authority_id=authority.id)

    all_comments = MuseumComment.objects.filter(
        museum__authority=authority
    ).order_by("-created_at")

    paginator = Paginator(all_comments, 3)
    page_number = request.GET.get("page")
    comments_page = paginator.get_page(page_number)

    museums_with_comments = []
    for museum in museums:
        comments = museum.comments.all().order_by("-created_at")
        museums_with_comments.append((museum, comments))

    return render(request, "museum/details.html", {
        "authority": authority,
        "museums_with_comments": museums_with_comments,
        "museums": museums,
        "comments_page": comments_page,
    })


# ==========================
# البحث
# ==========================
def search(request):
    query = request.GET.get('q', '').strip()

    authorities = Authority.objects.filter(name__icontains=query) if query else Authority.objects.none()
    museums = Museum.objects.filter(name__icontains=query) if query else Museum.objects.none()

    return render(request, 'museum/search_results.html', {
        'authorities': authorities,
        'museums': museums,
    })


# ==========================
# الحجز
# ==========================
@login_required
def add_booking(request, museum_id):
    museum = get_object_or_404(Museum, id=museum_id)
    booking, created = Booking.objects.get_or_create(user=request.user, museum=museum)

    if created:
        messages.success(request, "تم حجز المتحف بنجاح!")
    else:
        messages.info(request, "لقد قمت بحجز هذا المتحف مسبقًا.")

    return redirect('account:user_profile', user_name=request.user.username)


# ==========================
# مفضلة المتحف
# ==========================
@login_required
def add_museum_bookmark(request, museum_id):
    museum = get_object_or_404(Museum, id=museum_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, museum=museum)

    if created:
        messages.success(request, "تمت إضافة المتحف للمفضلة!")
    else:
        messages.info(request, "هذا المتحف موجود بالفعل في المفضلة")

    return redirect(request.META.get('HTTP_REFERER', '/'))
