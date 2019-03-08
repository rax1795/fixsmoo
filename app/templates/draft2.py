{% extends "base.html" %}
{% import 'bootstrap/wtf.html' as wtf %}

{% block app_content %}
    <h1>Register</h1>
    <div class="container">
        <div class="col-md-4 align-content-center">
            {{ wtf.quick_form(form) }}
        </div>
    </div>

{% endblock %}