from django.shortcuts import render, redirect
from .models import Authority, AuthorityType
from .forms import AuthorityForm, MuseumForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Museum


def add_authority(request):

    if request.method == "POST":
        form = AuthorityForm(request.POST, request.FILES)

        if form.is_valid():
            authority = form.save(commit=False)
            authority.owner = request.user
            authority.save()

            messages.success(request, "✔ تم إضافة الهيئة بنجاح")

            # التحويل لصفحة إضافة المتحف وتمرير ID الهيئة
            return redirect('add_museum', authority_id=authority.id)

    else:
        form = AuthorityForm()

    return render(request, 'museum/add_authority.html', {"form": form})


def all_authority(request):
    # قراءة نوع الفلترة من الرابط ؟type=1 مثلاً
    authority_type = request.GET.get("type")

    if authority_type:
        authorities = Authority.objects.filter(type_id=authority_type)
    else:
        authorities = Authority.objects.all().order_by("-id")

    # جلب الأنواع للفلترة
    types = AuthorityType.objects.all()

    return render(request, 'museum/all_authority.html', {
        "authorities": authorities,
        "types": types,
        "selected": authority_type,
    })

def add_museum(request, authority_id):
    authority = Authority.objects.get(id=authority_id)

    if request.method == "POST":
        form = MuseumForm(request.POST, request.FILES)

        if form.is_valid():
            museum = form.save(commit=False)
            museum.authority = authority
            museum.save()

            messages.success(request, "✔ تمت إضافة المتحف للهيئة بنجاح!")
            return redirect('add_museum', authority_id=authority_id)

    else:
        form = MuseumForm()

    return render(request, 'museum/add_museum.html', {
        "form": form,
        "authority": authority
    })


def all_del_museum(request):
    return render(request, 'museum/all_del_museum.html')


def booking(request):
    authorities = Authority.objects.all()
    museums = Museum.objects.all()
    context = {
        'authorities': authorities,
        'museums': museums,
    }
    return render(request, 'museum/booking.html', context)


def details(request):
    return render(request, 'museum/details.html')


def search(request):
    return render(request, 'museum/search.html')



def museums_by_authority(request, authority_id):
    museums = Museum.objects.filter(authority_id=authority_id)
    data = [{"id": m.id, "name": m.name} for m in museums]
    return JsonResponse(data, safe=False)




