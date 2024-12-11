from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import Gift, WishList
from app import db
from .forms import GiftForm

# Gifts Blueprint
gifts_bp = Blueprint('gifts', __name__)

# ADD GIFT ROUTE
@gifts_bp.route('/add/<int:wishlist_id>', methods=['GET', 'POST'])
@login_required # Must be logged in
def add_gift(wishlist_id):
    # Fetch wishlist
    wishlist = WishList.query.get_or_404(wishlist_id)

    # Check user permissions
    if current_user not in wishlist.collaborators:
        flash("Invalid permissions", "danger")
        return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist_id))

    # Add gift
    form = GiftForm()
    if form.validate_on_submit():
        # Check if wishlist has gift with duplicate name
        existing_gift = Gift.query.filter_by(name=form.name.data, wishlist_id=wishlist_id).first()
        if existing_gift:
            flash("GIft already exists", "danger")
            return redirect(url_for('gifts.add_gift', wishlist_id=wishlist_id))

        new_gift = Gift(
            name=form.name.data,
            price=form.price.data,
            link=form.link.data,
            description=form.description.data,
            priority=form.priority.data,
            wishlist_id=wishlist.id
        )
        db.session.add(new_gift)
        db.session.commit()

        # Success
        flash("Gift added successfully.", "success")
        return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist_id))

    return render_template('add_gift.html', form=form, wishlist=wishlist)

# EDIT GIFT ROUTE
@gifts_bp.route('/edit/<int:gift_id>', methods=['GET', 'POST'])
@login_required # Must be logged in
def edit_gift(gift_id):
    # Fetch gift
    gift = Gift.query.get_or_404(gift_id)
    wishlist = gift.wishlist

    # Check user permissions
    if current_user not in gift.wishlist.collaborators:
        flash("Invalid permissions", "danger")
        return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist.id))

    # Update gift with current gift properties
    form = GiftForm(obj=gift)
    if form.validate_on_submit():
        for g in wishlist.gifts:
            if g.id != gift.id:
                if g.name == form.name.data:
                    flash("Gift already exists", "danger")
                    return redirect(url_for('gifts.edit_gift', gift_id=gift.id))

        gift.name = form.name.data
        gift.price = form.price.data
        gift.link = form.link.data
        gift.description = form.description.data
        gift.priority = form.priority.data
        db.session.commit()

        # Redirect to wishlist
        flash("Gift successfully updated", "success")
        return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist.id))

    return render_template('edit_gift.html', form=form, gift=gift)

# DELETE GIFT ROUTE
@gifts_bp.route('/delete/<int:gift_id>', methods=['GET', 'POST'])
@login_required # Must be logged in
def delete_gift(gift_id):
    # Fetch gift
    gift = Gift.query.get_or_404(gift_id)
    wishlist = gift.wishlist

    # Check user permissions
    if current_user not in wishlist.collaborators:
        flash("Invalid permissions", "danger")
        return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist.id))

    # Delete gift
    db.session.delete(gift)
    db.session.commit()

    # Redirect to wishlist
    flash("Gift successfully deleted", "success")
    return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist.id))

# TOGGLE BOUGHT STATUS ROUTE
@gifts_bp.route('/toggle/<int:gift_id>', methods=['GET', 'POST'])
@login_required # Must be logged in
def toggle_gift(gift_id):
    # Fetch gift
    gift = Gift.query.get_or_404(gift_id)
    wishlist = gift.wishlist

    # Check user is not a collaborator
    if current_user in gift.wishlist.collaborators:
        flash("Invalid permissions", "danger")
        return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist.id))

    # Toggle bought status
    gift.bought = not gift.bought
    db.session.commit()

    # Redirect to wishlist
    flash("Gift status toggled successfully", "success")
    return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist.id))