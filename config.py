from flask import Flask, render_template, request, url_for, jsonify, redirect, flash, jsonify
devmode = True
if devmode:
    server = "http://localhost:5000/"
else:
    server = "http://52.37.251.245/"
app = Flask(__name__)