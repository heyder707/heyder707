import random
#from markdown2 import Markdown
from django.shortcuts import render
from django import forms
from django.http import HttpResponse

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def show_entry(request, entry_name):
    entry_name = entry_name.lower()
    if util.get_entry(entry_name) is not None:
        return render(request, "encyclopedia/entry.html", {
            "entry_name": entry_name,
            "content": convert_markdown_to_html(util.get_entry(entry_name))
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "Sorry, no entry found for that specific term."
        })

def search_entry(request):
    if request.method == "POST":
        query = request.POST["q"].lower()
        if query == "":
            return render(request, "encyclopedia/search.html", {
            "query": query,
            "search_results": None
            })
        saved_entries = [x.lower() for x in util.list_entries()]
        matching_entries = [s for s in saved_entries if query in s]
        if len(matching_entries) == 1 and query == matching_entries[0]:
            return render(request, "encyclopedia/entry.html", {
                "entry_name": query,
                "content": convert_markdown_to_html(util.get_entry(query))
            })
        else:
            return render(request, "encyclopedia/search.html", {
            "query": query,
            "search_results": matching_entries if len(matching_entries) >= 1 else None
            })
    return render(request, "encyclopedia/error.html", {
        "message": "Hmm, something went wrong."
    })


def create_entry(request):
    if request.method == "POST":
        new_entry_form = NewEntryForm(request.POST)
        if new_entry_form.is_valid():
            captcha = int(new_entry_form.cleaned_data["captcha"])
            if captcha != 3:
                return render(request, "encyclopedia/error.html", {
                    "message": "Failed to publish new entry (wrong captcha)."
                })
            saved_entries = saved_entries = [x.lower() for x in util.list_entries()]
            entry_title = new_entry_form.cleaned_data["entry_title"].lower()
            if entry_title in saved_entries:
                return render(request, "encyclopedia/error.html", {
                    "message": "Failed to publish new entry (already exists in Wiki database)."
                })
            entry_description = new_entry_form.cleaned_data["entry_description"]
            util.save_entry(entry_title, entry_description)
            return render(request, "encyclopedia/entry.html", {
                "entry_name": entry_title,
                "content": convert_markdown_to_html(util.get_entry(entry_title))
            })

        else:
            return render(request, "encyclopedia/create.html", {
            "new_entry_form": NewEntryForm()
        })
    
    return render(request, "encyclopedia/create.html", {
            "new_entry_form": NewEntryForm()
        })
    

def edit_entry(request, entry_name):
    if request.method == "GET":
        if entry_name is not None:
            entry_description = util.get_entry(entry_name)
            initial = {'entry_description': entry_description}
            return render(request, "encyclopedia/edit.html", {
                "entry_name": entry_name,
                "edit_form": EditForm(initial=initial)
            })
        else:
            return render(request, "encyclopedia/error.html", {
            "message": "Hmm, something went wrong."
        })
    else:
        edit_form = EditForm(request.POST)
        if edit_form.is_valid():
            captcha = int(edit_form.cleaned_data["captcha"])
            if captcha != 5:
                return render(request, "encyclopedia/error.html", {
                    "message": "Failed to edit entry (wrong captcha)."
                })
            new_description = edit_form.cleaned_data["entry_description"]
            util.save_entry(entry_name, new_description)
            return render(request, "encyclopedia/entry.html", {
                "entry_name": entry_name,
                "content": convert_markdown_to_html(util.get_entry(entry_name))
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "message": "Hmm, something went wrong."
            })


def random_entry(request):
    saved_entries = util.list_entries()
    random_int = random.randint(0, len(saved_entries) - 1)
    random_entry = saved_entries[random_int].lower()
    return render(request, "encyclopedia/entry.html", {
        "entry_name": random_entry,
        "content": convert_markdown_to_html(util.get_entry(random_entry))
    })


def convert_markdown_to_html(content):
    markdowner = Markdown()
    return markdowner.convert(content)


class NewEntryForm(forms.Form):
    entry_title = forms.CharField(label="Entry title",
        min_length=1,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': "Enter a descriptive title"}) #replaces default widget
        )
    entry_description = forms.CharField(
        label="Description (use Markdown language)",
        min_length=1,
        max_length=14000,
        widget=forms.Textarea(attrs={'placeholder': "What do you know about this specific subject?"})) #replaces default widget
    captcha = forms.IntegerField(
        label="Captcha: How much is 5 + 5 - 7 ? ")


class EditForm(forms.Form):
    entry_description = forms.CharField(label="Description (use Markdown language)",
        min_length=1, max_length=14000, widget=forms.Textarea)
    captcha = forms.IntegerField(label="Captcha: How much is 3 + 4 - 2 ? ")