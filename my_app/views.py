from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from requests.compat import quote_plus

from . import models

# Create your views here.
base_url = "https://sfbay.craigslist.org/search/?query={}&sort=rel&s={}&min_price={}&max_price={}"


def search(request):

    s = 0
    if request.GET.get("next"):
        s = request.GET.get("next").split("=")[1]

    if request.GET.get("prev"):
        s = request.GET.get("prev").split("=")[1]

    query = request.GET.get("query")


    new_search = request.POST.get("search") or query or ""
    min_price = request.POST.get('min_price', 0)
    max_price = request.POST.get('max_price')
    models.Search.objects.create(search=new_search)
    url = base_url.format(quote_plus(new_search), s, min_price, max_price)
    response = requests.get(url)


    soup = BeautifulSoup(response.text, features="html.parser")

    listings = soup.find_all("li", {"class": "result-row"})

    data = []
    image_url = "https://images.craigslist.org/{}_300x300.jpg"

    next_btn = url
    if soup.find(class_="button next"):
        next_btn = soup.find(class_="button next").get("href")

    prev_btn = url
    if soup.find(class_="button prev"):
        prev_btn = soup.find(class_="button prev").get("href")
    
    totalcount = ""
    if soup.find(class_="totalcount"):
        totalcount = soup.find(class_="totalcount").text

    rangeFrom = ""
    if soup.find(class_="rangeFrom"):
        rangeFrom = soup.find(class_="rangeFrom").text

    rangeTo = ""
    if soup.find(class_="rangeTo"):
        rangeTo = soup.find(class_="rangeTo").text


    for post in listings:
        title = post.find(class_="result-title hdrlnk").text
        url = post.find("a").get("href")

        if post.find(class_="result-price"):
            price = post.find(class_="result-price").text
        else:
            price = "N/A"
        if post.find(class_="result-image gallery"):
            img_id = post.find(
                class_="result-image gallery").get("data-ids").split(",")[0][2:]
            img_url = image_url.format(img_id)
        else:
            img_url = "https://www.stma.org/wp-content/uploads/2017/10/no-image-icon.png"
        data.append((title, url, price, img_url))

    stuff_for_frontend = {
        "search": new_search,
        "data": data,
        "next_btn": next_btn,
        "prev_btn": prev_btn,
        "rangeFrom": rangeFrom,
        "rangeTo": rangeTo,
        "totalcount": totalcount
    }
    return render(request, "my_app/search.html", stuff_for_frontend)