from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .models import WishList, Family, User
from app import db
from .forms import WishListForm, AddCollaboratorForm

# Wishlist Blueprint
wishlist_bp = Blueprint('wishlist', __name__)

# DASHBOARD ROUTE
@wishlist_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required # Must be logged in
def dashboard():
    # Fetch family
    family = Family.query.get_or_404(current_user.family_id)

    # Group by collaborators for display
    wishlists_grouped = {}
    for user in family.users:
        wishlists_grouped[user.username] = []
        for wishlist in user.wishlists:
            wishlists_grouped[user.username].append(wishlist)


    return render_template('dashboard.html', family=family, wishlists_grouped=wishlists_grouped)

# CREATE WISHLIST ROUTE
@wishlist_bp.route('/create', methods=['GET', 'POST'])
@login_required # Must be logged in
def create_wishlist():
    form = WishListForm()
    if form.validate_on_submit():
        # Check for unique name
        for ws in current_user.wishlists:
            if form.name.data == ws.name:
                flash("You already have a wishlist with this name", "danger")
                return redirect(url_for('wishlist.dashboard'))
            
        # Create new wishlist
        new_wishlist = WishList(name=form.name.data, family_id=current_user.family_id)
        new_wishlist.collaborators.append(current_user)

        db.session.add(new_wishlist)
        db.session.commit()

        # Redirect to dashboard
        flash("Wishlist created successfully", "success")
        return redirect(url_for('wishlist.dashboard'))

    return render_template('create_wishlist.html', form=form)

# VIEW WISHLIST ROUTE
@wishlist_bp.route('/view/<int:wishlist_id>', methods=['GET', 'POST'])
@login_required # Must be logged in
def view_wishlist(wishlist_id):
    wishlist = WishList.query.get_or_404(wishlist_id)
    family = Family.query.get_or_404(current_user.family_id)

    # Check for user access
    if family.id != wishlist.family_id:
        # Invalid access
        flash("You do not have access to this wishlist", "danger")
        return redirect(url_for('wishlist.dashboard'))

    # Fetch gifts and check if user owns wishlist (for bought toggle)
    is_collaborator = current_user in wishlist.collaborators

    # Populate AddCollaboratorForm with non-collaborators
    add_collaborator_form = AddCollaboratorForm()
    non_collaborators = [
        member for member in family.users if member not in wishlist.collaborators
    ]
    add_collaborator_form.collaborator.choices = [
        (user.id, user.username) for user in non_collaborators
    ]

    all_added = False
    if not add_collaborator_form.collaborator.choices:
        all_added = True

    # Handle adding a collaborator
    if is_collaborator and add_collaborator_form.validate_on_submit():
        collaborator = User.query.get(add_collaborator_form.collaborator.data)
        if collaborator in wishlist.collaborators:
            flash("This user is already a collaborator", "info")
        else:
            wishlist.collaborators.append(collaborator)
            db.session.commit()
            flash(f"{collaborator.username} has been added as a collaborator", "success")
        return redirect(url_for('wishlist.view_wishlist', wishlist_id=wishlist.id, all_added=all_added))

    # Filtering gifts
    filter_option = request.args.get("filter", "all")
    if filter_option == "bought":
        gifts = [gift for gift in wishlist.gifts if gift.bought]
    elif filter_option == "to_buy":
        gifts = [gift for gift in wishlist.gifts if not gift.bought]
    else:
        gifts = wishlist.gifts

    # Order by priority (descending) > Name
    gifts = sorted(gifts, key=lambda gift: (-gift.priority, gift.name.lower()))

    return render_template(
        'view_wishlist.html', 
        wishlist=wishlist, 
        gifts=gifts, 
        is_collaborator=is_collaborator,
        add_collaborator_form=add_collaborator_form,
        filter_option=filter_option,
        all_added=all_added
    )


# DELETE WISHLIST ROUTE
@wishlist_bp.route('/delete/<int:wishlist_id>', methods=['GET', 'POST'])
@login_required # Must be logged in
def delete_wishlist(wishlist_id):
    wishlist = WishList.query.get_or_404(wishlist_id)

    # Check user permissions
    if current_user not in wishlist.collaborators:
        flash("You do not have access to this wishlist", "danger")
        return redirect(url_for('wishlist.dashboard'))
    
    # Delete wishlist
    db.session.delete(wishlist)
    db.session.commit()

    # Redirect to dashboard
    flash("Wishlist deleted successfully", "success")
    return redirect(url_for('wishlist.dashboard'))