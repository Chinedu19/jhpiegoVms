from operator import length_hint
from flask import Blueprint, redirect, url_for, render_template,flash, make_response,current_app, json
from flask_login import login_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask.globals import request
from .model import Vehicle,Users,Repairs,Fuel
from . import db
from sqlalchemy import text
import pdfkit
from datetime import datetime
import re

admin = Blueprint('admin', __name__)
states = ["Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "FCT - Abuja", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara"]
regularExp = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$' #regex for email

sql_sum_by_month = text('SELECT MONTHNAME(period), YEAR(period), SUM(total_Qty_purchased_ngn), SUM(opening_km), SUM(closing_km) FROM fuel GROUP BY YEAR(period), MONTH(period)')
sql_sum_by_year = text('SELECT YEAR(period), SUM(total_Qty_purchased_ngn), SUM(opening_km), SUM(closing_km) FROM fuel GROUP BY YEAR(period), MONTH(period)')
def allowed_files(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in current_app.config['ALLOWED_IMAGE_EXTENSION']:
        return True
    else:
        return False





def allowed_file_size(filesize):
    if int(filesize) <= current_app.config['MAX_IMAGE_FILESIZE']:
        return True
    else:
        return False

def getCurrentTime():
    return datetime.now().strftime('%Y-%m-%d')
    

def get_fuel_consumption_data(tableName, duration):
    finalData = {}
    sql=""
    months = {1:"January", 2:"February", 3:"March", 4:"April", 5:"May", 6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
    if duration == 'month':
        sql = sql_sum_by_month
        result = db.engine.execute(sql)
        for row in result:
            print(row)
            month = row[0]
            year = row[1]
            ngn =  float(row[2])
            opening =  int(row[3])
            closing =  int(row[4])
            km_covered =  closing - opening
            finalData[f"{month} {year}"]= [ngn, km_covered]

        keys=list(finalData.keys())
        values=list(finalData.values())
        # diction = {'time': keys, 'amount': values, "km_covered": }
        return [keys,values]
    elif duration == '30' or duration == '60':
        sql = text(f'SELECT * FROM {tableName} WHERE period BETWEEN CURDATE() - INTERVAL {duration} DAY AND SYSDATE()')

        result = db.engine.execute(sql)
        for row in result:
            year,month,day = row.period.strftime('%Y-%m-%d').split("-")
            ngn =  float(row.total_Qty_purchased_ngn)
            opening =  int(row.opening_km)
            closing =  int(row.closing_km)
            km_covered =  closing - opening
            month = int(month)
            day = int(day)
            finalData[f"{day} {months[month][0:3]}"]= [ngn, km_covered]
    
    
        keys=list(finalData.keys())
        values=list(finalData.values())

        # diction = {'time': keys, 'amount': values, "km_covered": }
        return [keys,values]
    elif duration == 'year':
        sql = sql_sum_by_year
        result = db.engine.execute(sql)
        for row in result:
            year = row[0]
            ngn =  float(row[1])
            opening =  int(row[2])
            closing =  int(row[3])
            km_covered =  closing - opening
            finalData[f"{year}"]= [ngn, km_covered]

        keys=list(finalData.keys())
        values=list(finalData.values())
        # diction = {'time': keys, 'amount': values, "km_covered": }
        return [keys,values]



# Error Pages
@admin.app_errorhandler(404)
@login_required
def page_not_found(e):
    return render_template('admin/404errorPage.html',user=current_user), 404


# Home
@admin.route('/')
@login_required
def admin_home():
    user_count = Users.query.filter_by(isDeleted = 0).count()
    vehicle_count = Vehicle.query.filter_by(isDeleted = 0).count()
    repair_count = Repairs.query.filter_by(isDeleted = 0).count()
    fuel_count = Fuel.query.filter_by(isDeleted = 0).count()
    info = [vehicle_count,repair_count,fuel_count,user_count]
    return render_template("admin/dash.html", card = info,user=current_user)


# Chart Json
@admin.route('/chart_data/<string:duration>')
def chart_info(duration=30, chartID = 'chart_ID', chart_type = 'line', chart_height = 500):
    chart_fuel_data = get_fuel_consumption_data('fuel', duration)
    data = [{'message' : "No records available"}]
    amountData = [x[0] for x in chart_fuel_data[1]]
    millageData = [x[1] for x in chart_fuel_data[1]]
    if amountData and millageData:
        data = [
            {'chart':{"renderTo": chartID, "type": chart_type, "height": chart_height},
        'series': [{"name": 'Amount', "data": amountData}, {"name": 'Millage', "data": millageData}],
        'title' : {"text": 'Jhpiego Fuel Consumption'},
        'xAxis' : {'categories': chart_fuel_data[0]},
        'yAxis' : {"title": {"text": 'Fuel Price'}, 'max': max(amountData)},
        'plotOptions': {'line': {'dataLabels': {'enabled': True},'enableMouseTracking': False}}
            }]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    if amountData and millageData:
        return response
    else:
        return response, 404



# Users Crud
@admin.route('/users')
@login_required
def users():
    user = Users.query.filter_by(isDeleted = 0).order_by(Users.id)
    return render_template("admin/users.html", users=user, user=current_user)

@admin.route('/users/add',methods=['GET', 'POST'])
@login_required
def add_users():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        phone = request.form.get('tel')
        role = request.form.get('role')
        pword = request.form.get('passw')
        cpassW = request.form.get('cPassw')

        fields = [email,first_name,last_name,phone,pword,cpassW]
        reg = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$' #regex for email
        phone_reg ='^\+[1-9]{1}[0-9]{3,14}$' #regex for phone numer
        for field in fields:
            print(field)
            if len(field) == 0:
                flash('All fields are required', category='error')
        
        if pword != cpassW:
            flash("Passwords and confirm password do not match", category='error')
        elif not re.search(reg, email):
            flash('mail is incorrect', category='error')
        elif not re.search("^(?:\d{11}|\w+@\w+\.\w{2,3})$", phone):
            flash('phone format is incorrect', category='error')
        elif len(pword) <6:
            flash("Password must be at least 6 characters", category='error')
        elif len(first_name) < 3:
            flash("First name must be more than 3 characters", category='error')
        elif len(last_name) < 3:
            flash("last name must be more than 3 characters", category='error')
        else:
            user = Users.query.filter_by(email=email).first()
            if user:
                flash('Email already exists', category='error')
            else:
                if phone.startswith('0'):
                    phone = phone.replace("0", "+234",1)
                new_user = Users(email=email, first_name=first_name,last_name=last_name, password=generate_password_hash(pword, method="sha256"), phone_number=phone, role=role, isDeleted = 0)
                db.session.add(new_user)
                db.session.commit()
                flash('Account created', category='success')
                return render_template('admin/add_users.html',user=current_user)
    return render_template('admin/add_users.html',user=current_user)

@admin.route('/users/promote/<string:mail>')
@login_required
def promote_users(mail):
    if re.search(regularExp, mail):
        user = Users.query.filter_by(email=mail,isDeleted = 0).first()
        if user:
            user.role = 1
            db.session.commit()
            flash(user.first_name +' has been promoted', category='success')
            return redirect(url_for("admin.users"))
        else:
            flash('User does not exist', category='error')
            return redirect(url_for("admin.users"))
    else:
        flash('User does not exist', category='error')
        return redirect(url_for("admin.users"))

@admin.route('/users/demote/<string:mail>')
@login_required
def demote_users(mail):
    if re.search(regularExp, mail):
        user = Users.query.filter_by(email=mail,isDeleted = 0).first()
        if user:
            user.role = 0
            db.session.commit()
            flash(user.first_name +' has been demoted', category='success')
            return redirect(url_for("admin.users"))
        else:
            flash('User does not exist', category='error')
            return redirect(url_for("admin.users"))
    else:
        flash('User does not exist', category='error')
        return redirect(url_for("admin.users"))

@admin.route('/users/delete/<string:mail>', methods=['GET','POST'])
@login_required
def delete_user(mail):
    if re.search(regularExp, mail):
        user = Users.query.filter_by(email=mail,isDeleted = 0).first()
        if user:
            user.isDeleted = 1
            db.session.commit()
            flash('User deleted successful', category='success')
            return redirect(url_for("admin.users"))
        else:
            flash('User does not exists', category='error')
            return redirect(url_for("admin.users"))
    else:
        flash('User does not exists', category='error')
        return redirect(url_for("admin.vehicles"))


# Fleet CRUD

@admin.route('/fleet')
@login_required
def vehicles():
    car = Vehicle.query.filter_by(isDeleted = 0).order_by(Vehicle.id)
    return render_template("admin/vehicles.html", vehicles = car,user=current_user)

@admin.route('/fleet/add', methods=['GET','POST'])
@login_required
def add_vehicles():
    
    if request.method == 'POST':
        reg_no = request.form.get('reg')
        make = request.form.get('make')
        model_ = request.form.get('model')
        color = request.form.get('color')
        state = request.form.get('state')

        fields = [reg_no, make, model_, color, state]

        # Checking if any field is empty
        for field in fields:
            if len(field) == 0:
                flash('All fields are required', category='error')
        if len(reg_no) < 8:
            flash('Registration number cannot be less than 8', category='error')
        else:
            car = Vehicle.query.filter_by(reg_no=reg_no).first()
            if car:
                flash('Vehicle already exists', category='error')
            else:
                new_car = Vehicle(reg_no=reg_no, brand=make,brand_model=model_, color=color, state=state, isDeleted = 0)
                db.session.add(new_car)
                db.session.commit()
                flash('Vehicle added', category='success')
                return redirect(url_for("admin.vehicles"))
        

    return render_template("admin/addVehicle.html", states = states,user=current_user)

@admin.route('/fleet/delete/<string:reg_number>', methods=['GET','POST'])
@login_required
def delete_vehicles(reg_number):
    if len(reg_number) == 8:
        car = Vehicle.query.filter_by(reg_no=reg_number, isDeleted = 0).first()
        if car:
            car.isDeleted = 1
            db.session.commit()
            flash('Vehicle delete successful', category='success')
            return redirect(url_for("admin.vehicles"))
        else:
            flash('Vehicle does not exists', category='error')
            return redirect(url_for("admin.vehicles"))
    else:
        flash('Vehicle does not exists', category='error')
        return redirect(url_for("admin.vehicles"))
            
@admin.route('/fleet/edit/<string:reg_number>', methods=['GET','POST'])
@login_required
def edit_vehicles(reg_number):
    if request.method == 'POST':
        reg_no = request.form.get('reg')
        make = request.form.get('make')
        model_ = request.form.get('model')
        color = request.form.get('color')
        state = request.form.get('state')

        fields = [reg_no, make, model_, color, state]
        print(fields)
        # Checking if any field is empty
        for field in fields:
            if len(field) == 0:
                flash('All fields are required', category='error')
        if len(reg_no) < 8:
            flash('Registration number cannot be less than 8', category='error')
        else:
            car = Vehicle.query.filter_by(reg_no=reg_no, isDeleted = 0).first()
            if not car:
                flash('Vehicle does not exists', category='error')
            else:
                car.brand = make
                car.brand_model = model_
                car.color = color
                car.state = state
                try:
                    db.session.commit()
                    flash('Vehicle edit successful', category='success')
                    return redirect(url_for("admin.vehicles"))
                except:
                    return "An Issue occured"
    else:
        if len(reg_number) == 8:
            car = Vehicle.query.filter_by(reg_no=reg_number, isDeleted = 0).first()
            if car:
                return render_template("admin/editVehicle.html", states= states, vehicle=car,user=current_user)
            else:
                flash('Vehicle does not exists', category='error')
                return redirect(url_for("admin.vehicles"))
        else:
            flash('Vehicle does not exists', category='error')
            return redirect(url_for("admin.vehicles"))

@admin.route('/report')
@login_required
def view_summary():
    # user = Users.query.filter_by(isDeleted = 0).order_by(Users.id)
    # car = Vehicle.query.filter_by(isDeleted = 0).order_by(Vehicle.id)
    # fuel = Fuel.query.join(Vehicle, Fuel.vehicle == Vehicle.id).add_columns(Fuel.id, Fuel.vehicle,Fuel.period,Fuel.opening_km,Fuel.closing_km,Fuel.avg_price,Fuel.total_Qty_purchased_ltrs,Fuel.total_Qty_purchased_ngn, Vehicle.id,Vehicle.reg_no).filter(Fuel.id==Vehicle.id)
    # repair = Repairs.query.join(Vehicle, Repairs.vehicle == Vehicle.id).add_columns(Repairs.id, Repairs.vehicle,Repairs.period,Repairs.last_service_mileage, Repairs.current_service_mileage,Repairs.km_covered,Repairs.total_cost, Vehicle.id,Vehicle.reg_no).filter(Repairs.id==Vehicle.id)
    # # print(fuel, repair)
    return render_template("admin/summary.html", user=current_user)


@admin.route('/report/get/<string:info>')
@login_required
def download_json(info):
    record= None
    header = None
    if info == 'vehicles':
        record = Vehicle.query.filter_by(isDeleted = 0).order_by(Vehicle.id)

        header = ['Vehicle', 'Period', 'Last Mileage Served', 'Current Mileage', 'Km Covered']
    elif info == 'users':
        record = Users.query.filter_by(isDeleted = 0).order_by(Users.id)
        header = ['Name', 'Email', 'Phone Number','Role']
    elif info == 'fuel':
        record = Fuel.query.join(Vehicle, Fuel.vehicle == Vehicle.id).add_columns(Fuel.id, Fuel.vehicle,Fuel.period,Fuel.opening_km,Fuel.closing_km,Fuel.avg_price,Fuel.total_Qty_purchased_ltrs,Fuel.total_Qty_purchased_ngn, Vehicle.id,Vehicle.reg_no).filter(Fuel.id==Vehicle.id)
        header = ['Vehicle', 'Period', 'Opening Km', 'Closing Km', 'KM Covered', 'Total Quantity (l)', 'Total Amount', 'Avg. Price']
    elif info == 'repairs':
        record = Repairs.query.join(Vehicle, Repairs.vehicle == Vehicle.id).add_columns(Repairs.id, Repairs.vehicle,Repairs.period,Repairs.last_service_mileage, Repairs.current_service_mileage,Repairs.km_covered,Repairs.total_cost, Vehicle.id,Vehicle.reg_no).filter(Repairs.id==Vehicle.id)
        header = ['Vehicle', 'Period','Last Mileage Served', 'Current Mileage', 'Km Covered', 'Total Cost']
    # options = {'enable-local-file-access': ""}
    
    if record is not None and header is not None:
        rendered = render_template("admin/table.html", record=record, user=current_user, header = header, info=info.capitalize())
        return rendered

@admin.route('/report/download/<string:info>')
@login_required
def download_summary(info):
    record= None
    header = None
    if info == 'vehicles':
        record = Vehicle.query.filter_by(isDeleted = 0).order_by(Vehicle.id)

        header = ['Vehicle', 'Period', 'Last Mileage Served', 'Current Mileage', 'Km Covered']
    elif info == 'users':
        record = Users.query.filter_by(isDeleted = 0).order_by(Users.id)
        header = ['Name', 'Email', 'Phone Number','Role']
    elif info == 'fuel':
        record = Fuel.query.join(Vehicle, Fuel.vehicle == Vehicle.id).add_columns(Fuel.id, Fuel.vehicle,Fuel.period,Fuel.opening_km,Fuel.closing_km,Fuel.avg_price,Fuel.total_Qty_purchased_ltrs,Fuel.total_Qty_purchased_ngn, Vehicle.id,Vehicle.reg_no).filter(Fuel.id==Vehicle.id)
        header = ['Vehicle', 'Period', 'Opening Km', 'Closing Km', 'KM Covered', 'Total Quantity (l)', 'Total Amount', 'Avg. Price']
    elif info == 'repairs':
        record = Repairs.query.join(Vehicle, Repairs.vehicle == Vehicle.id).add_columns(Repairs.id, Repairs.vehicle,Repairs.period,Repairs.last_service_mileage, Repairs.current_service_mileage,Repairs.km_covered,Repairs.total_cost, Vehicle.id,Vehicle.reg_no).filter(Repairs.id==Vehicle.id)
        header = ['Vehicle', 'Period','Last Mileage Served', 'Current Mileage', 'Km Covered', 'Total Cost']
    options = {'enable-local-file-access': ""}
    
    if record is not None and header is not None:
        rendered = render_template("admin/table.html", record=record, user=current_user, header = header, info=info.lower())        
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        pdf = pdfkit.from_string(rendered, False, configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
        return response



@admin.route('/repairs')
@login_required
def repairs():
    repair = Repairs.query.join(Vehicle, Repairs.vehicle == Vehicle.id).add_columns(Repairs.id, Repairs.vehicle,Repairs.period,Repairs.last_service_mileage, Repairs.current_service_mileage,Repairs.km_covered,Repairs.total_cost, Vehicle.id,Vehicle.reg_no)
    return render_template("admin/repairs.html",repairs=repair, user=current_user)

@admin.route('/repairs/add',methods=['GET','POST'])
@login_required
def add_repairs_data():
    if request.method == 'POST':
        req_id = request.form.get('vehicle')
        period = request.form.get('date')
        last_mileage = request.form.get('last_mileage')
        mileage = request.form.get('mileage')
        total_cost = request.form.get('total_cost')
        km_covered = request.form.get('km_covered')
        comments = request.form.get('comments')
        numeric_fields = [last_mileage,mileage,total_cost,km_covered]
        for number in numeric_fields:
            try:
                if int(number) < 1:
                    flash("No field can be left as 0", 'error')
            except ValueError:
                if float(number) < 1:
                    flash("No field can be left as 0", 'error')
            except Exception:
                flash("An error occured please contact developer", 'error')
            
        if period > getCurrentTime():
            flash("Date cannot be more than today's date", 'error')
        else:
            new_data =""
            if request.files and request.files['attachment'].filename != "":
                print(request.files)
                print(request.url)
                attachment = request.files['attachment']
                import os
                if not allowed_files(attachment.filename):
                    flash("The file attached is not allowrd", 'error')
                    return redirect(url_for("admin.add_repairs_data"))
                else:
                    filename = secure_filename(attachment.filename)
                    basedir = os.path.abspath(os.path.dirname(__file__))
                    path = os.path.join(basedir,current_app.config['IMAGE_UPLOADS'], filename)
                    attachment.save(path)
                    new_data = Repairs(vehicle=req_id, period=period,isServiced=1,last_service_mileage=last_mileage,current_service_mileage=mileage,km_covered=km_covered,total_cost=total_cost,comments=comments,attachment=filename)
            else:
                new_data = Repairs(vehicle=req_id, period=period,isServiced=1,last_service_mileage=last_mileage,current_service_mileage=mileage,km_covered=km_covered,total_cost=total_cost,comments=comments)
            try:
                db.session.add(new_data)
                db.session.commit()
                flash('Details added', category='success')
            except Exception:
                flash('Information was reject please check and try again', category='error')    
    car = Vehicle.query.filter_by(isDeleted = 0).order_by(Vehicle.id)
    return render_template("admin/add_repairs.html",vehicles=car, user=current_user)

@admin.route('/consumption')
@login_required
def consumption():
    fuel = Fuel.query.join(Vehicle, Fuel.vehicle == Vehicle.id).add_columns(Fuel.id, Fuel.vehicle,Fuel.period,Fuel.opening_km,Fuel.closing_km,Fuel.avg_price,Fuel.total_Qty_purchased_ltrs,Fuel.total_Qty_purchased_ngn, Vehicle.id,Vehicle.reg_no)
    return render_template("admin/fuel.html",fuel_consumptions=fuel, user=current_user)

@admin.route('/consumption/add',methods=['GET','POST'])
@login_required
def add_consumption():
    if request.method == 'POST':
        req_id = request.form.get('vehicle')
        period = request.form.get('date')
        opening_km = request.form.get('opening_km')
        closing_km = request.form.get('closing_km')
        ngn_purchased = request.form.get('ngn_purchased')
        ltrs_purchased = request.form.get('ltrs_purchased')
        avg_price = request.form.get('avg_price')
        comments = request.form.get('comments')
        fields = [req_id, period,opening_km,closing_km,ngn_purchased, ltrs_purchased,avg_price,comments]
        # if request.files:
        #     attachment = request.files['attachment']
        if int(opening_km) < 1:
            flash("Opening KM cannot be less than 1", 'error')
        if period > getCurrentTime():
            flash("Date cannot be more than today's date", 'error')
        elif int(closing_km) < 1:
            flash("Closing KM cannot be less than 1", 'error')
        elif int(opening_km) >= int(closing_km):
            flash("Closing KM cannot be less than Opening KM", 'error')
        elif int(ngn_purchased) < 100:
            flash("This valuecannot be less than 100", 'error')
        elif int(ltrs_purchased) < 1:
            flash("Litres purchased cannot be less than 1", 'error')
        elif float(avg_price) < 1:
            flash("Avg cannot be less than 1", 'error')
        else:
            new_data =""
            if request.files['attachment']:
                
                attachment = request.files['attachment']
                import os
                if attachment.filename == "":
                    flash("file needs a name", 'error')
                    return redirect(url_for("admin.consumption"))
                if not allowed_files(attachment.filename):
                    flash("The file attached is not allowrd", 'error')
                    return redirect(url_for("admin.consumption"))
                else:
                    filename = secure_filename(attachment.filename)
                    basedir = os.path.abspath(os.path.dirname(__file__))
                    path = os.path.join(basedir,current_app.config['IMAGE_UPLOADS'], filename)
                    attachment.save(path)
                    new_data = Fuel(vehicle=req_id, period=period, opening_km=opening_km, closing_km=closing_km, total_Qty_purchased_ltrs=ltrs_purchased, total_Qty_purchased_ngn=ngn_purchased, avg_price=avg_price,comments=comments, attachment=filename)
            else:
                new_data = Fuel(vehicle=req_id, period=period, opening_km=opening_km, closing_km=closing_km, total_Qty_purchased_ltrs=ltrs_purchased, total_Qty_purchased_ngn=ngn_purchased, avg_price=avg_price,comments=comments)
            try:
                db.session.add(new_data)
                db.session.commit()
                flash('Details added', category='success')
            except Exception:
                flash('Information was rejected please check and try again', category='error')
            return redirect(url_for("admin.consumption"))
    car = Vehicle.query.filter_by(isDeleted = 0).order_by(Vehicle.id)
    return render_template("admin/add_fuel.html",vehicles=car, user=current_user)