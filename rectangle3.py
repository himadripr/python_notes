from flask import Flask
from flask import jsonify
from flask import send_file
from flask import request
from xlrd import open_workbook
from flask import render_template
from werkzeug import secure_filename
import os
import zipfile
import io
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from rectpack import newPacker
import rectpack.packer as packer
import rectpack.skyline as skyline
import rectpack.guillotine as guillotine
import rectpack.maxrects as maxrects
import rectpack.waste as waste
from rectpack.geometry import Rectangle
import timeit
import random
from datetime import datetime
from werkzeug import SharedDataMiddleware
from flask import send_from_directory

from PIL import Image, ImageDraw, ImageFont


path=[];
UPLOAD_FOLDER='E:/Junks/Chinmay/New folder/Uploads';
def zip(dst):
		foo = zipfile.ZipFile(dst, 'w')
		for p in path:
			foo.write(p)
		foo.close();
		
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['xlsx', 'xls'])

def rect_draw(x1,y1,x2,y2,d):
    d.line([x1,y1,x1,y2], fill=(0,0,0), width=5)
    d.line([x1,y1,x2,y1], fill=(0,0,0), width=5)
    d.line([x2,y2,x1,y2], fill=(0,0,0), width=5)
    d.line([x2,y2,x2,y1], fill=(0,0,0), width=5)
    d.rectangle([x1,y1,x2,y2],fill=(245,222,179),outline =(0,0,0))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.add_url_rule('/uploads/<filename>', 'uploaded_file',build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {'/uploads':  app.config['UPLOAD_FOLDER']})

@app.route('/check/<name>')
def checkServer(name):
	return name;

@app.route('/upload')
def upload_file():
   return render_template('upload.html');
   
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file1():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if not allowed_file(file.filename):
            return 'Upload excel file!';
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return checkName1(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
    return 'Upload again!';
	  
@app.route('/uploadfile/<path:filename>')
def uploaded_file(filename):
    f1=filename.rsplit('/', 1)[0]+'/';
    f2=filename.rsplit('/', 1)[1]
    file=send_from_directory(f1,f2)
    return file;
    
	
@app.route('/cut/<path:name>')
def checkName1(name):	
	wb = open_workbook(name)
	f_dr='E:/Junks/Chinmay/New folder/Rectangles/';
	sheet=wb.sheets()[0]
	
	number_of_rows = sheet.nrows
	number_of_columns = sheet.ncols
	
	length=(sheet.cell(1,1).value)
	breadth=(sheet.cell(2,1).value)
	blade=(sheet.cell(3,1).value)
	
	rectangles=[];
	for k in range(6,number_of_rows):
		quantity=int((sheet.cell(k,3).value))
		if(quantity>1):
			for n in range(0,quantity):
				r=(int((sheet.cell(k,1).value))+blade,int((sheet.cell(k,2).value))+blade,str((sheet.cell(k,0).value))+'_'+str(n));
				rectangles.append(r)
		else:
			r=(int((sheet.cell(k,1).value))+blade,int((sheet.cell(k,2).value))+blade,str((sheet.cell(k,0).value)));
			rectangles.append(r)
	
	packerr = packer.newPacker(bin_algo=packer.PackingBin.Global,rotation=True,pack_algo = guillotine.GuillotineBssfSas)
	for r in rectangles:
		packerr.add_rect(*r)
		
	packerr.add_bin(length,breadth,count=float("inf"))
	packerr.pack()
	all_rects = packerr.rect_list()
	for rect in all_rects:
		b, x, y, w, h, rid = rect
	for sheet in range(0,len(packerr)):
            h = packerr[sheet].height + 400
            w = packerr[sheet].width + 400
            
            txt = Image.new('RGB', (int(w),int(h)), (255,255,255))
            fnt = ImageFont.truetype("arial.ttf",50)

            d = ImageDraw.Draw(txt)
            d.line([200,200,int(w)-200,200], fill=(0,0,0), width=5)
            d.line([200,200,200,int(h)-200], fill=(0,0,0), width=5)
            d.line([200,int(h)-200,int(w)-200,int(h)-200], fill=(0,0,0), width=5)
            d.line([int(w)-200,200,int(w)-200,int(h)-200], fill=(0,0,0), width=5)
            for i in range(0,int(w)-400+1,200):

                d.line([i+200,185,i+200,215], fill=(0,0,0), width=5)
                wi,hi = fnt.getsize(str(i))
                d.text((i+200-wi/2,185-5-hi), str(i), font=fnt, fill=(50,55,25))

                d.line([i+200,h-185,i+200,h-215], fill=(0,0,0), width=5)
                wi,hi = fnt.getsize(str(i))
                d.text((i+200-wi/2,h-180), str(i), font=fnt, fill=(50,55,25))

            for i in range(0,int(h)-400+1,200):
                d.line([185,i+200,215,i+200], fill=(0,0,0), width=5)
                wi,hi = fnt.getsize(str(i))
                d.text((185-wi-5,i+200-hi/2), str(i), font=fnt, fill=(50,55,25))

                d.line([w-185,i+200,w-215,i+200], fill=(0,0,0), width=5)
                wi,hi = fnt.getsize(str(i))
                d.text((w-180,i+200-hi/2), str(i), font=fnt, fill=(50,55,25))

            for r in packerr[sheet]:
                rect_draw(r.x+200,r.y+200,r.x+r.width+200,r.y+r.height+200,d)
                wi,hi = fnt.getsize(r.rid)
                d.text((r.x+r.width/2-wi/2+200,r.y+r.height/2-hi/2+200),r.rid,font=fnt, fill=(50,55,25))
        #     rect_draw(900,900,1200,1250,d)
            txt.save(f_dr+str(sheet)+'.jpg')
            path.append(f_dr+str(sheet)+'.jpg')

	
	text_file = open("E:/Junks/Chinmay/New folder/cutting.txt", "w")
	text_file.write(str(packerr.rect_list()))
	path.append("E:/Junks/Chinmay/New folder/cutting.txt")
	text_file.close()
	dst='E:/Junks/Chinmay/New folder/temp.zip';
	zip(dst)
	del path[:]
	return send_file(dst,attachment_filename='Cutting_Plan.zip',as_attachment=True)

@app.route('/cut/panel-details', , methods=['POST'])
def cut_panel_details():	
	
	f_dr='E:/Junks/Chinmay/New folder/Rectangles/';
	arr = json.loads(request.form['jsondata'])
    req_data = arr[0]
    typ = req_data['type']
    length = req_data['sheet_length']
    breadth = req_data['sheet_breadth']
    blade = req_data['blade_thickness']
    detailsArray = req_data['details']
    detailsArraylength = len(detailsArray)
	
	
	rectangles=[];
	for k in range(detailsArraylength):
		quantity=int(detailsArray[k]['quantity'])
		if(quantity>1):
			for n in range(0,quantity):
				r=(int((detailsArray[k]['length']))+blade,int((detailsArray[k]['height']))+blade,str((detailsArray[k]['unique_id']))+'_'+str(n));
				rectangles.append(r)
		else:
			r=(int((detailsArray[k]['length']))+blade,int((detailsArray[k]['height']))+blade,str((detailsArray[k]['unique_id'])));
			rectangles.append(r)
	
	packerr = packer.newPacker(bin_algo=packer.PackingBin.Global,rotation=True,pack_algo = guillotine.GuillotineBssfSas)
	for r in rectangles:
		packerr.add_rect(*r)
		
	packerr.add_bin(length,breadth,count=float("inf"))
	packerr.pack()
	all_rects = packerr.rect_list()
	for rect in all_rects:
		b, x, y, w, h, rid = rect
	for sheet in range(0,len(packerr)):
            h = packerr[sheet].height + 400
            w = packerr[sheet].width + 400
            
            txt = Image.new('RGB', (int(w),int(h)), (255,255,255))
            fnt = ImageFont.truetype("arial.ttf",50)

            d = ImageDraw.Draw(txt)
            d.line([200,200,int(w)-200,200], fill=(0,0,0), width=5)
            d.line([200,200,200,int(h)-200], fill=(0,0,0), width=5)
            d.line([200,int(h)-200,int(w)-200,int(h)-200], fill=(0,0,0), width=5)
            d.line([int(w)-200,200,int(w)-200,int(h)-200], fill=(0,0,0), width=5)
            for i in range(0,int(w)-400+1,200):

                d.line([i+200,185,i+200,215], fill=(0,0,0), width=5)
                wi,hi = fnt.getsize(str(i))
                d.text((i+200-wi/2,185-5-hi), str(i), font=fnt, fill=(50,55,25))

                d.line([i+200,h-185,i+200,h-215], fill=(0,0,0), width=5)
                wi,hi = fnt.getsize(str(i))
                d.text((i+200-wi/2,h-180), str(i), font=fnt, fill=(50,55,25))

            for i in range(0,int(h)-400+1,200):
                d.line([185,i+200,215,i+200], fill=(0,0,0), width=5)
                wi,hi = fnt.getsize(str(i))
                d.text((185-wi-5,i+200-hi/2), str(i), font=fnt, fill=(50,55,25))

                d.line([w-185,i+200,w-215,i+200], fill=(0,0,0), width=5)
                wi,hi = fnt.getsize(str(i))
                d.text((w-180,i+200-hi/2), str(i), font=fnt, fill=(50,55,25))

            for r in packerr[sheet]:
                rect_draw(r.x+200,r.y+200,r.x+r.width+200,r.y+r.height+200,d)
                wi,hi = fnt.getsize(r.rid)
                d.text((r.x+r.width/2-wi/2+200,r.y+r.height/2-hi/2+200),r.rid,font=fnt, fill=(50,55,25))
        #     rect_draw(900,900,1200,1250,d)
            txt.save(f_dr+str(sheet)+'.jpg')
            path.append(f_dr+str(sheet)+'.jpg')

	
	text_file = open("E:/Junks/Chinmay/New folder/cutting.txt", "w")
	text_file.write(str(packerr.rect_list()))
	path.append("E:/Junks/Chinmay/New folder/cutting.txt")
	text_file.close()
	dst='E:/Junks/Chinmay/New folder/temp.zip';
	zip(dst)
	del path[:]
	return send_file(dst,attachment_filename='Cutting_Plan.zip',as_attachment=True)





	
	
if __name__ == '__main__':

 app.run(host='0.0.0.0',threaded=True)
