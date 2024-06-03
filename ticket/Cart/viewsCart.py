import json

from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from ticket.models import Event, EventTicket
from django.contrib import messages


def cart_view(request):
    if request.user.is_authenticated:
        total_cost = 0
        event_tickets = request.session.get('cart_items', [])
        for event_ticket in event_tickets:
            ticket_price = event_ticket['event'].get('ticket_price', 0)
            total_cost += event_ticket['quantity'] * ticket_price
            total_cost = round(total_cost, 2)
    else:
        messages.warning(request, 'You must be logged in to view this page.')
        return redirect('login')

    context = {
        "title": "Cart",
        "event_tickets": event_tickets,
        "total_cost": total_cost,
    }
    return render(request, "cart.html", context)


def cart_add(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.user.is_authenticated:
        if request.method == 'POST':
            ticket_quantity = int(request.POST.get('ticket_quantity', 1))
            if ticket_quantity > event.tickets:
                messages.warning(request, 'Insufficient tickets available')
                return redirect('event_detail', event_id=event_id)

            if event.image:
                temp_ticket = {
                    'event': {
                        'id': event.id,
                        'eventName': event.eventName,
                        'image': event.image.url,
                        'ticket_price': float(event.ticket_price) if event.ticket_price is not None else 0.0,
                        'currency': event.currency,
                    },
                    'quantity': ticket_quantity,
                }
            else:
                temp_ticket = {
                    'event': {
                        'id': event.id,
                        'eventName': event.eventName,
                        'ticket_price': float(event.ticket_price)if event.ticket_price is not None else 0.0,
                        'currency': event.currency,
                    },
                    'quantity': ticket_quantity,
                }
            cart_items = request.session.get('cart_items', [])
            for item in cart_items:
                if item['event']['id'] == event_id:
                    item['quantity'] += ticket_quantity
                    request.session.save()
                    messages.success(request, 'Item added to cart successfully')
                    return redirect('event_detail', event_id=event_id)
            cart_items.append(temp_ticket)
            request.session['cart_items'] = cart_items
            request.session.save()

            messages.success(request, 'Item added to cart successfully')
            return redirect('event_detail', event_id=event_id)
    else:
        messages.warning(request, 'You must be logged in to add ticket to the cart.')
        return redirect('login')


def cart_update(request, event_id):
    user = request.user
    event_tickets = request.session.get('cart_items', [])

    if request.method == 'POST':
        action = request.POST.get('action')
        for event_ticket in event_tickets:
            if event_ticket['event']['id'] == event_id:
                if action == 'add':
                    event_ticket['quantity'] += 1
                elif action == 'remove':
                    event_ticket['quantity'] -= 1
                if event_ticket['quantity'] == 0:
                    event_tickets.remove(event_ticket)
                    messages.success(request, 'Item removed from cart successfully')
    request.session['cart_items'] = event_tickets
    request.session.save()
    return redirect('cart_view')


def cart_delete(request, event_id):
    user = request.user
    if request.method == 'POST':
        event_tickets = request.session.get('cart_items', [])
        for event_ticket in event_tickets:
            if event_ticket['event']['id'] == event_id:
                event_tickets.remove(event_ticket)
                request.session['cart_items'] = event_tickets
                request.session.save()
        messages.success(request, 'Item removed from cart successfully')

    return redirect('cart_view')


@transaction.atomic
def process_checkout(request):
    user = request.user
    in_cart_tickets = request.session.get('cart_items', [])
    if not in_cart_tickets:
        messages.warning(request, 'No tickets to checkout.')
        return redirect('cart_view')
    else:
        for purchased_ticket in in_cart_tickets:
            event = Event.objects.get(id=purchased_ticket['event']['id'])
            if purchased_ticket['quantity'] > event.tickets:
                messages.warning(request, 'Insufficient tickets available')
                return redirect('cart_view')
            else:
                event.tickets -= purchased_ticket['quantity']
                event.save()
                purchased_event_ticket = EventTicket.objects.create(
                    user=user,
                    event=event,
                    quantity=purchased_ticket['quantity'],
                )
                purchased_event_ticket.save()

        request.session['cart_items'] = []
        request.session.save()
        messages.success(request, 'Thank you for your purchase!')

    return redirect('checkout_success')


def checkout_success(request):
    user = request.user
    purchased_tickets = EventTicket.objects.filter(user=user)
    context = {
        'title': 'Tickets',
        'purchased_tickets': purchased_tickets,
    }
    return render(request, 'tickets.html', context)
