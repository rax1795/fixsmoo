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

  <!-- <div class="form-group">
            <label for="photo">Any photos of the issue?</label>-->
            <!-- <input type="password" class="form-control" id="InputPassword" placeholder="Password"> -->
            <!-- {{ form.photo( class_ ='form-control') }}
            {% for error in form.unit.errors %}
            <span style="color: red;">[{{ error }}]</span>
            {% endfor %}
        </div> --> 