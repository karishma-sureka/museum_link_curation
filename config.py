from flask import Flask, render_template, request, url_for, jsonify, redirect, flash, jsonify
devmode = True
app = Flask(__name__)