from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from .mongodb import clients_collection, users_collection
from bson.objectid import ObjectId
from datetime import datetime, timedelta

def login_page(request):

    if request.session.get("logged_in"):
        return redirect("/dashboard/")

    if request.method == "POST":

        username = request.POST.get("username").strip().lower()
        password = request.POST.get("password")

        user = users_collection.find_one(
            {
                "username": username
            }
        )

        if user and check_password(
            password,
            user["password"]
        ):

            request.session["logged_in"] = True
            request.session["username"] = username
            request.session["role"] = user.get(
                "role",
                "user"
            )

            return redirect("/dashboard/")

        messages.error(
            request,
            "Invalid username or password"
        )

    return render(
        request,
        "login.html"
    )


def dashboard(request):

    if not request.session.get("logged_in"):
        return redirect("/")

    total_clients = (
        clients_collection.count_documents({"owner": request.session["username"]})
    )

    clients = list(
        clients_collection.find({"owner": request.session["username"]})
    )

    expiring_domains = 0
    expiring_clients = []

    today = datetime.today()
    for client in clients:

        try:

            expiry_date = datetime.strptime(
                client.get("domain_expiry"),
                "%Y-%m-%d"
            )

            days_left = (
                expiry_date - today
            ).days

            if 0 <= days_left <= 30:

                expiring_domains += 1

                expiring_clients.append(
        {
            "client_name":
            client["client_name"],

            "domain_name":
            client["domain_name"],

            "days_left":
            days_left
        }
    )

        except:

            pass

    total_revenue = 0

    for client in clients:

        try:

            total_revenue += int(
                client.get(
                    "renewal_charge",
                    0
                )
            )

        except:

            pass



    return render(

        request,

        'dashboard.html',

        {
    "total_clients": total_clients,
    "total_revenue": total_revenue,
    "expiring_domains": expiring_domains,
    "expiring_clients": expiring_clients
}

    )


def add_client(request):

    if not request.session.get("logged_in"):
        return redirect("/")

    if request.method == "POST":

        client_data = {
            "owner": request.session["username"],
            "client_name": request.POST.get("client_name"),
            "website": request.POST.get("website"),
            "domain_name": request.POST.get("domain_name"),
            "domain_expiry": request.POST.get("domain_expiry"),
            "email_username": request.POST.get("email_username"),
            "hosting_username": request.POST.get("hosting_username"),
            "hosting_password": request.POST.get("hosting_password"),
            "renewal_charge": request.POST.get("renewal_charge")

        }

        clients_collection.insert_one(client_data)
        messages.success(
    request,
    "Client added successfully"
)
        return redirect("/clients/")

    return render(request, "add_client.html")

def view_clients(request):

    if not request.session.get("logged_in"):
        return redirect("/")

    search = request.GET.get("search")

    if search:

        clients = list(
            clients_collection.find(
                {
                    "owner": request.session["username"],
                    "client_name":
                    {
                        "$regex": search,
                        "$options": "i"
                    }
                }
            )
        )

    else:

        clients = list(
            clients_collection.find({ "owner": request.session["username"]})
        )

    for client in clients:
        client["id"] = str(client["_id"])

    return render(
        request,
        "clients.html",
        {
            "clients": clients
        }
    )

def delete_client(request, id):

    if not request.session.get("logged_in"):
        return redirect("/")

    clients_collection.delete_one(
        {
            "_id": ObjectId(id),
            "owner": request.session["username"]
        }
    )
    messages.success(
    request,
    "Client deleted successfully"
)
    return redirect("/clients/")

def edit_client(request, id):

    if not request.session.get("logged_in"):
        return redirect("/")

    client = clients_collection.find_one(
        {
            "_id": ObjectId(id),
            "owner": request.session["username"]
        }
    )

    if request.method == "POST":

        clients_collection.update_one(

            {
                "_id": ObjectId(id),
                "owner": request.session["username"]
            },

            {
                "$set": {

                    "client_name":
                    request.POST.get("client_name"),

                    "website":
                    request.POST.get("website"),

                    "domain_name":
                    request.POST.get("domain_name"),

                    "domain_expiry":
                    request.POST.get("domain_expiry"),

                    "renewal_charge":
                    request.POST.get("renewal_charge")

                }
            }

        )

        return redirect("/clients/")

    client["id"] = str(client["_id"])

    return render(
        request,
        "edit_client.html",
        {
            "client": client
        }
    )
def change_password(request):

    if not request.session.get("logged_in"):
        return redirect("/")

    if request.method == "POST":

        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")

        username = request.session["username"]

        user = users_collection.find_one(
            {
                "username": username
            }
        )

        if check_password(
            old_password,
            user["password"]
        ):

            users_collection.update_one(

                {
                    "username": username
                },

                {
                    "$set": {
                        "password":
                        make_password(
                            new_password
                        )
                    }
                }

            )

            messages.success(
                request,
                "Password changed successfully"
            )

            return redirect("/dashboard/")

        else:

            messages.error(
                request,
                "Old password is incorrect"
            )

    return render(
        request,
        "change_password.html"
    )
def domains(request):

    if not request.session.get("logged_in"):
        return redirect("/")

    domains = list(
        clients_collection.find(
            {
                "owner":
                request.session["username"]
            }
        )
    )

    return render(
        request,
        "domains.html",
        {
            "domains": domains
        }
    )
def settings(request):

    if not request.session.get("logged_in"):
        return redirect("/")

    return render(
        request,
        "settings.html"
    )
def logout(request):

    request.session.flush()

    return redirect("/")

def add_user(request):

    if not request.session.get("logged_in"):
        return redirect("/")

    if request.session.get("role") != "admin":
        return redirect("/dashboard/")

    if request.method == "POST":

        username = request.POST.get("username").strip().lower()

        password = request.POST.get("password")

        hashed_password = make_password(
            password
        )

        users_collection.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "role": "user"
            }
        )

        messages.success(
            request,
            "User created successfully"
        )

        return redirect("/users/")

    return render(
        request,
        "add_user.html"
    )

def view_users(request):

    if not request.session.get("logged_in"):
        return redirect("/")
    if request.session.get("role") != "admin":
        return redirect("/dashboard/")

    users = list(
        users_collection.find()
    )

    for user in users:
        user["id"] = str(user["_id"])

    return render(
        request,
        "users.html",
        {
            "users": users
        }
    )

def delete_user(request, id):

    if not request.session.get("logged_in"):
        return redirect("/")
    if request.session.get("role") != "admin":
        return redirect("/dashboard/")

    users_collection.delete_one(
        {
            "_id": ObjectId(id)
        }
    )
    messages.success(
    request,
    "User deleted successfully"
)
    return redirect("/users/")