import pandas as pd
import io
import openpyxl
from flask import send_file
from app.models import User, Car, Booking, Contacts, Groups, Renewal
from flask_login import current_user

def download_report_group(group, start_date, end_date, group_bookings, commission_amount):
    bookings_amount = group.stats(start_date, end_date)[1]
    rented_days = group.stats(start_date, end_date)[2]
    money_spent = group.stats(start_date, end_date)[3]
    if int(commission_amount) > 0:
        commission_due = money_spent * (float(commission_amount) / 100)
    # Create the summary data as a list of lists
    summary_data = [
        ['Numero prenotazioni', bookings_amount],
        ['Giorni noleggiati', rented_days],
        [current_user.currency, money_spent],
        [f'Commissione del {commission_amount}% su {current_user.currency} {money_spent}', commission_due]
    ]

    # Create a DataFrame for the bookings data
    bookings_data = [{
        'Prenotazione ID': booking.id, 
        'Targa Auto': booking.car.plate, 
        'Modello Auto': booking.car.model,
        'Prezzo': booking.money, 
        'Data Inizio': booking.start_datetime.strftime('%d-%m %H:%M'), 
        'Data Fine': booking.end_datetime.strftime('%d-%m %H:%M'),
        'Cliente': (Contacts.query.filter_by(id=booking.contact_id).first()).full_name if booking.contact_id else ''
    } for booking in group_bookings]
    
    bookings_df = pd.DataFrame(bookings_data)

    # Write the summary data and bookings data to the same Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write summary data to the top of the Excel sheet
        for row_num, row_data in enumerate(summary_data):
            pd.DataFrame([row_data]).to_excel(writer, index=False, header=False, startrow=row_num, sheet_name='Report')
        
        # Write the bookings data starting from a few rows below the summary
        bookings_df.to_excel(writer, index=False, startrow=len(summary_data) + 2, sheet_name='Report')
    
    output.seek(0)
    file_name = f'resoconto gruppo {group.name} dal {start_date} al {end_date}.xlsx'
    
    return send_file(
        output,
        download_name=file_name,
        as_attachment=True
    )

def download_report_general(start_date, end_date, user_bookings, rented_days, money_spent):
    bookings_amount = len(user_bookings)
    # Create the summary data as a list of lists
    summary_data = [
        ['Numero prenotazioni', bookings_amount],
        ['Giorni noleggiati', rented_days],
        [current_user.currency, money_spent],
    ]

    # Create a DataFrame for the bookings data
    bookings_data = [{'Prenotazione ID': booking.id, 'Targa Auto': booking.car.plate, 'Modello Auto': booking.car.model, f'{current_user.measurement_unit}': booking.km,
                            'Prezzo': booking.money, 'Data Inizio': booking.start_datetime.strftime('%d-%m %H:%M'), 'Data Fine': booking.end_datetime.strftime('%d-%m %H:%M'),
                            'Cliente': (Contacts.query.filter_by(id=booking.contact_id).first()).full_name if booking.contact_id else '', 
                            'Gruppo': booking.group.name if booking.group else '', 
                            'Nota': booking.note} for booking in user_bookings]
    
    bookings_df = pd.DataFrame(bookings_data)

    # Write the summary data and bookings data to the same Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Write summary data to the top of the Excel sheet
        for row_num, row_data in enumerate(summary_data):
            pd.DataFrame([row_data]).to_excel(writer, index=False, header=False, startrow=row_num, sheet_name='Report')
        
        # Write the bookings data starting from a few rows below the summary
        bookings_df.to_excel(writer, index=False, startrow=len(summary_data) + 2, sheet_name='Report')
    
    output.seek(0)
    file_name = f'resoconto prenotazioni dal {start_date} al {end_date}.xlsx'
    
    return send_file(
        output,
        download_name=file_name,
        as_attachment=True
    )