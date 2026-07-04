from django.shortcuts import render


def error_404(request, exception):
    return render(request, "error_404.html", status=404)

def error_403(request, exception):
    return render(request, "error_403.html", status=403)