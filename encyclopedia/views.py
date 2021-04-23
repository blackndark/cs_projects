import markdown2
import random
from django import forms
from django.shortcuts import render
from django.core.files.storage import default_storage

from . import util

# Create a new class to handle form inputs via Django forms. For new page.
class NewPageForm(forms.Form):
    page_title = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Title'}))
    page_content = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Content'}))

# Create a second class to handle form inputs via Django forms. For edit page.
class EditPageForm(forms.Form):
    #page_title = forms.CharField(label="Entry Title", disabled=True )
    edit_content = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control'}))

# Main index page, lists all the entries.
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Entry pages, renders content of each entry or if the entry is not defined renders error page.
def entry_page(request, title):
    if not util.get_entry(title):
        return render(request, "encyclopedia/error.html", {
        "error_title" : title,
        "page_exist" : util.get_entry(title)
        })

    return render(request, "encyclopedia/title.html", {
        "encyclopedia_entry" : markdown2.markdown(util.get_entry(title)),
        "title" : title.capitalize()
    })

# Takes the search term and renders the related entry page. 
# If there is no page renders a page with entries entries that have the query as a substring.
def search_func(request):
    search = request.GET.get("q")
    if util.get_entry(search):
        return render(request, "encyclopedia/title.html", {
            "encyclopedia_entry" : markdown2.markdown(util.get_entry(search)),
            "title" : search.upper()
        })
    else:
        entry_list = util.list_entries()
        new_list = [entry for entry in entry_list if search.lower() in entry.lower()]
        return render(request, "encyclopedia/index.html", {
            "entries": new_list
        })

# Creates new entry via title and textarea to enter Markdown content. 
# Takes the user to the new entry page or renders an error page if the entry is already created.
def new_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            page_title = form.cleaned_data["page_title"]
            page_content = form.cleaned_data["page_content"]
            filename = f"entries/{page_title}.md"
            if default_storage.exists(filename):
                return render(request, "encyclopedia/error.html", {
                    "error_title" : page_title.upper(),
                    "page_exist" : default_storage.exists(filename)
                })
            else:
                util.save_entry(page_title, page_content)
                return render(request, "encyclopedia/title.html", {
                    "encyclopedia_entry" : markdown2.markdown(page_content),
                    "title" : page_title
                })

    return render(request, "encyclopedia/new_page.html", {
        "form" : NewPageForm()
    })


# Give ability to edit an entry with a prepopulated form with current content. Then give ability to save changes.
def edit_page(request, title):
    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            #page_title = form.cleaned_data["page_title"]
            edit_content = form.cleaned_data["edit_content"]
            util.save_entry(title.capitalize(), edit_content)
            return render(request, "encyclopedia/title.html", {
                "encyclopedia_entry" : markdown2.markdown(edit_content),
                "title" : title.capitalize()
            })
    
    current_entry = util.get_entry(title)
    return render(request, "encyclopedia/edit_page.html", {
        "title" : title.capitalize(),
        "form" : EditPageForm(initial={"edit_content" : current_entry})
    })


# Take the user to a random entry page.
def random_page(request):
    entry_list = util.list_entries()
    random_entry = random.choice(entry_list)
    random_entry_content = util.get_entry(random_entry)
    html_random_entry_content = markdown2.markdown(random_entry_content)
    return render(request, "encyclopedia/title.html", {
        "encyclopedia_entry" : html_random_entry_content,
        "title" : random_entry
    })

