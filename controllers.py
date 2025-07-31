from flask import Flask, render_template, redirect, request,flash,url_for
from flask import current_app as app
from datetime import datetime
from application.models import db, ParkingSpot
from sqlalchemy import or_
import matplotlib.pyplot as plt
import os

from .models import *
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form.get("password")
        this_user = User.query.filter_by(username=username).first()
        if this_user:
            if this_user.password ==password:
                if this_user.type == "admin":
                    return redirect("/admindashhome")
                return redirect(f"/userdash/{this_user.id}")
            return render_template("incorrect_p.html")
        return render_template("not_exist.html")
    return render_template("signin.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        address = request.form["address"]
        pincode = request.form["pincode"]
        user_name= User.query.filter_by(username=username).first()
        user_email = User.query.filter_by(email=email).first()
        if user_name or user_email:
            return render_template("already.html")
        else:
            user= User(username=username, email=email, password=password, address=address, pincode=pincode)
            db.session.add(user)
            db.session.commit()
        return redirect(f"/userdash/{user.id}")
    return render_template("signup.html")

@app.route("/userdash/<int:user_id>")
def user_dash(user_id):
    lots = ParkingLot.query.all()
    this_user= User.query.filter_by(id=user_id).first()
    return render_template("userdash.html",lots=lots, this_user=this_user)

@app.route("/admindashhome")
def admindashhome():
    users = User.query.filter(User.type!="admin").all()
    all_lots = ParkingLot.query.all()
    return render_template("admindashhome.html", users=users,lots=all_lots)

@app.route("/admindashusers")
def admindashusers():
    users = User.query.filter(User.type!="admin").all()
    return render_template("admindashusers.html", users=users)



@app.route("/newparkinglot", methods=["GET","POST"])
def addlot():
    this_user = User.query.filter_by(type="admin").first()
    if request.method == "POST":
        locname = request.form.get("locname")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        price = float(request.form.get("price"))
        maxspots = int(request.form.get("maxspots"))
        new_lot = ParkingLot(locname=locname, address=address, pincode=pincode,price=price,maxspots=maxspots)
        db.session.add(new_lot)
        db.session.commit()

        spots = [ParkingSpot(lot_id=new_lot.id, spot_number=i,status="A")
            for i in range(1, maxspots + 1)]
        db.session.add_all(spots)
        db.session.commit()
        return redirect("/admindashhome")
    return render_template("newparkinglot.html")

@app.route("/editparkinglot/<int:lot_id>", methods=["GET","POST"])
def editlot(lot_id):
    this_user = User.query.filter_by(type="admin").first()
    lot = ParkingLot.query.get_or_404(lot_id)
    if request.method == "POST":
        lot.locname = request.form.get("locname")
        lot.address = request.form.get("address")
        lot.pincode = request.form.get("pincode")
        lot.price = request.form.get("price")
        lot.maxspots = request.form.get("maxspots")
        db.session.commit()
        return redirect("/admindashhome")
    return render_template("editparkinglot.html",lot=lot,this_user=this_user)



@app.route("/bookinghistory/<int:user_id>")
def booking_history(user_id):
    this_user = User.query.get_or_404(user_id) 
    occupied_spots = ParkingSpot.query.filter_by(status="O", customer_id=user_id).all()
    return render_template("bookinghistory.html",occupied_spots=occupied_spots, user_id=user_id, this_user=this_user)



@app.route("/free_spot/<int:user_id>/<int:spot_id>", methods=["POST"])
def free_spot(user_id, spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status == "O" and spot.customer_id == user_id:
        spot.status = "A"
        spot.customer_id = None
        spot.vehicle_number = None
        spot.time_of_parking = None
        spot.estimated_cost = None
        db.session.commit()
    return redirect(f"/bookinghistory/{user_id}")


@app.route("/viewparkingspot/<int:spot_id>", methods=["GET","POST"])
def editspot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if request.method == "POST":
        if spot.status =="O":
            flash("Cannot delete an occupied parking spot!", "danger")
            return redirect(f"/viewparkingspot/{id}")
        db.session.delete(spot)
        db.session.commit()
        flash("Spot deleted successfully.", "success")
        return redirect("/admindashhome")
    return render_template("viewparkinglot.html",spot=spot)


@app.route("/userlotdetails/<int:lot_id>/<int:user_id>", methods=["GET", "POST"])
def user_lot_details(lot_id, user_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        spot_id = int(request.form["sid"])
        vehicle_number = request.form["vehicle_number"]
        time_of_parking = int(request.form["time_of_parking"])

        spot = ParkingSpot.query.get_or_404(spot_id)
        spot.customer_id = user_id
        spot.vehicle_number = vehicle_number
        spot.time_of_parking = time_of_parking
        spot.estimated_cost = lot.price * time_of_parking
        spot.status = "O"  # Occupied

        db.session.commit()
        return redirect(f"/confirm/{user_id}")

    return render_template("userlotdetails.html",lot=lot,spots=spots,this_user=user)



@app.route("/bookparkingspot", methods=["GET", "POST"])
def book_parking_spot():
    if request.method == "POST":
        spot_id = request.form.get("sid")
        lot_id = request.form.get("lid")
        user_id = request.form.get("uid")
        vehicle_number = request.form.get("vno")

        spot = ParkingSpot.query.get(spot_id)
        if spot and spot.status == 'A':
            spot.status = 'O' 
            spot.customer_id = user_id
            spot.vehicle_number = vehicle_number
            db.session.commit()
            return redirect("/userdash")  
        else:
            return "Spot is not available", 400

    return render_template("bookparkingspot.html")

@app.route("/confirm/<int:user_id>", methods=["GET"])
def confirm_booking(user_id):
    this_user= User.query.filter_by(id=user_id).first()
    seats = request.args.getlist("seats")  
    return render_template("confirm.html", seats=seats,this_user=this_user)



@app.route("/lotdetails/<int:lot_id>", methods=["GET", "POST"])
def lot_details(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()

    selected_spot = request.form.get("selected_spot")
    total_cost = None

    if selected_spot and request.method == "POST":
        spot = ParkingSpot.query.get_or_404(selected_spot)
        spot.vehicle_number = request.form["vno"]
        spot.time_of_parking = int(request.form["time"])
        spot.estimated_cost = spot.time_of_parking * lot.price
        spot.status = 'O'
        db.session.commit()
        total_cost = spot.estimated_cost

    return render_template("lotdetails.html",lot=lot,spots=spots,selected_spot=selected_spot,total_cost=total_cost)


@app.route("/viewspot/<int:lot_id>/<int:spot_id>")
def view_spot_details(lot_id, spot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spot = ParkingSpot.query.get_or_404(spot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    total_cost = lot.price * spot.time_of_parking
    if spot.status != 'O':
        # Redirect back if spot is not occupied
        return redirect(url_for('lotdetails', lot_id=lot_id))

    return render_template("viewoccupiedspot.html", spot=spot, lot=lot,spots=spots,total_cost=total_cost)


@app.route("/deleteparkinglot/<int:lot_id>", methods=["POST"])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    ParkingSpot.query.filter_by(lot_id=lot_id).delete()
    db.session.delete(lot)
    db.session.commit()
    return redirect("/admindashhome")


@app.route("/usersearch")
def user_search():
    search_word = request.args.get("search", "").strip()
    key = request.args.get("key", "lot")  
    user_id = request.args.get("user_id", type=int)
    results = []
    if key == "lot":
        results = ParkingLot.query.filter(or_(ParkingLot.locname.ilike(f"%{search_word}%"),
                ParkingLot.address.ilike(f"%{search_word}%"))).all()

    return render_template("userresults.html",results=results,key=key,search_word=search_word, user_id=user_id)



@app.route("/adminsearch")
def admin_search():
    search_word = request.args.get("search", "").strip()
    key = request.args.get("key", "all")
    results = {"users": [], "lots": []}
    if key in ["user","both"]:
        results["users"] = User.query.filter(
            User.username.ilike(f"%{search_word}%")).all()
    if key in ["lot","both"]:
        results["lots"] = ParkingLot.query.filter(or_(ParkingLot.locname.ilike(f"%{search_word}%"),
                ParkingLot.address.ilike(f"%{search_word}%"))).all()
    return render_template("adminresults.html",results=results,search_word=search_word,key=key)

@app.route("/admindashusers/<int:user_id>")
def admin_dash_users(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("userdetails.html", user=user)



@app.route('/adminsummary')
def summary():
    lots = ParkingLot.query.all()
    lot_names = [lot.locname for lot in lots]
    revenue_data = [sum(spot.estimated_cost or 0 for spot in lot.spots) for lot in lots]
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    plt.figure(figsize=(4, 4))
    plt.pie(revenue_data, labels=lot_names, autopct='%1.1f%%')
    plt.title("Revenue by Lot")
    plt.savefig("static/revenue_chart.png")
    plt.close()
    plt.figure(figsize=(4, 4))
    plt.bar(['Available', 'Occupied'], [available_spots, occupied_spots], color=['green', 'red'])
    plt.title("Parking Spot Status")
    plt.savefig("static/status_chart.png")
    plt.close()

    return render_template('adminsummary.html')

