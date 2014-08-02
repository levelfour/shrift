//
//  ViewController.swift
//  ShriftTrainer
//
//  Created by Tsutsumi Fukumu on 8/3/14.
//  Copyright (c) 2014 ***. All rights reserved.
//

import UIKit
import QuartzCore

class ViewController: UIViewController {
	let SCREEN_WIDTH = UIScreen.mainScreen().bounds.width
	let SCREEN_HEIGHT = UIScreen.mainScreen().bounds.height
	let SERVER_URL = "http://localhost:5000/upload"
	var toolbar: UIToolbar!
	var canvas: UIImageView!
	var textbox: UITextField!
	var touchPoint: CGPoint!
	
	override func viewDidLoad() {
		super.viewDidLoad()
		
		toolbar = UIToolbar(frame: CGRect(x: 0, y: UIApplication.sharedApplication().statusBarFrame.size.height, width: SCREEN_WIDTH, height: 44))
		self.view.addSubview(toolbar)
		
		canvas = UIImageView(frame: CGRect(x: (SCREEN_WIDTH-400)/2, y: (SCREEN_HEIGHT-400)/2-100, width: 400, height: 400))
		canvas.backgroundColor = .whiteColor()
		canvas.layer.borderColor = UIColor.blackColor().CGColor
		canvas.layer.borderWidth = 2.0
		self.view.addSubview(canvas)
		
		let titleLabel = UILabel(frame: CGRect(x: 0, y: 0, width: 180, height: 80))
		titleLabel.text = "ShriftTrainer"
		titleLabel.textAlignment = NSTextAlignment.Center
		let title = UIBarButtonItem(customView: titleLabel)
		let spacer = UIBarButtonItem(barButtonSystemItem: UIBarButtonSystemItem.FlexibleSpace, target: self, action: nil)
		let trashBtn = UIBarButtonItem(barButtonSystemItem: UIBarButtonSystemItem.Trash, target: self, action: "clearCanvas")
		let actionBtn = UIBarButtonItem(barButtonSystemItem: UIBarButtonSystemItem.Action, target: self, action: "recognize")
		let items: NSMutableArray = NSMutableArray(array: [actionBtn, spacer, title, spacer, trashBtn])
		toolbar.setItems(items, animated: false)
		
		let description = UILabel(frame: CGRect(x: (SCREEN_WIDTH-600)/2, y: canvas.frame.origin.y-100, width: 600, height: 100))
		description.text = "黒枠の中に文字を書いてください"
		description.textAlignment = NSTextAlignment.Center
		description.font = UIFont(name: "HiraKakuProN-W3", size: 28)
		self.view.addSubview(description)
		
		textbox = UITextField(frame: CGRect(x: (SCREEN_WIDTH-400)/2, y: canvas.frame.origin.y+canvas.frame.height+50, width: 400, height: 60))
		textbox.placeholder = "識別対象"
		textbox.borderStyle = .Bezel
		textbox.font = UIFont(name: "HiraKakuProN-W3", size: 28)
		self.view.addSubview(textbox)
		
		let submitBtn = UIButton.buttonWithType(.Custom) as UIButton
		submitBtn.frame = CGRect(x: (SCREEN_WIDTH-100)/2, y: textbox.frame.origin.y+textbox.frame.height+30, width: 100, height: 40)
		submitBtn.setTitle("送信", forState: UIControlState.Normal)
		submitBtn.setTitle("送信", forState: UIControlState.Selected)
		submitBtn.setTitleColor(.blackColor(), forState: .Normal)
		submitBtn.setTitleColor(.grayColor(), forState: .Selected)
		submitBtn.layer.borderColor = UIColor.grayColor().CGColor
		submitBtn.layer.borderWidth = 2.0
		submitBtn.layer.cornerRadius = 7.5
		submitBtn.addTarget(self, action: "recognize", forControlEvents: UIControlEvents.TouchUpInside)
		self.view.addSubview(submitBtn)
	}
	
	override func didReceiveMemoryWarning() {
		super.didReceiveMemoryWarning()
		// Dispose of any resources that can be recreated.
	}
	
	func clearCanvas() {
		canvas.image = nil
	}
	
	func saveImage() -> NSString {
		// save to /Application/Document
		let image = UIImageJPEGRepresentation(canvas.image, 1.0)
		let path: NSString = NSSearchPathForDirectoriesInDomains(.DocumentDirectory, .UserDomainMask, true)[0] as NSString
		
		// save image with current time as name
		let now = NSDate()
		let dateFormatter = NSDateFormatter()
		dateFormatter.locale = NSLocale(localeIdentifier: "ja_JP")
		dateFormatter.dateFormat = "yyyy_MM_dd_HH_mm_ss"
		
		let fullpath = path.stringByAppendingPathComponent(dateFormatter.stringFromDate(now).stringByAppendingString(".jpg"))
		image?.writeToFile(fullpath, atomically: true)
		
		return fullpath
	}
	
	func requestWithImageFile(filename: NSString) {
		let url = NSURL(string: SERVER_URL)
		let boundary = NSString(format: "%d", arc4random() % 10000000)
		let config = NSURLSessionConfiguration.defaultSessionConfiguration()
		config.HTTPAdditionalHeaders = ["Content-Type": NSString(format: "multipart/form-data; boundary=%@", boundary)]
		var request = NSMutableURLRequest(URL: url)
		let session = NSURLSession(configuration: config)
		
		let image = NSData(contentsOfFile: filename)
		
		if image != nil {
			let post = NSMutableData.data()
			post.appendData(NSString(format: "--%@\r\n", boundary).dataUsingEncoding(NSUTF8StringEncoding))
			post.appendData(NSString(string: "Content-Disposition: form-data;").dataUsingEncoding(NSUTF8StringEncoding))
			post.appendData(NSString(format: "name=\"%@\";", "file").dataUsingEncoding(NSUTF8StringEncoding))
			post.appendData(NSString(format: "filename=\"%@\"\r\n", filename).dataUsingEncoding(NSUTF8StringEncoding))
			post.appendData(NSString(string: "Content-Type: image/jpeg\r\n\r\n").dataUsingEncoding(NSUTF8StringEncoding))
			post.appendData(image)
			post.appendData(NSString(string: "\r\n").dataUsingEncoding(NSUTF8StringEncoding))
			post.appendData(NSString(format: "--%@--\r\n", boundary).dataUsingEncoding(NSUTF8StringEncoding))
			
			request.HTTPMethod = "POST"
			request.HTTPBody = post
			let task: NSURLSessionDataTask = session.dataTaskWithRequest(request, completionHandler: { data, request, error in println(NSString(format: "<result=\"%@\">", NSString(data: data, encoding: NSUTF8StringEncoding))) })
			task.resume()
		} else {
			let alert = UIAlertView(title: "Alert", message: "draw something in canvas first", delegate: self, cancelButtonTitle: "OK")
			alert.show()
		}
	}
	
	func recognize() {
		let filename: NSString = saveImage()
		requestWithImageFile(filename)
	}
	
	override func touchesBegan(touches: NSSet!, withEvent event: UIEvent!) {
		// save the beginning point of touch
		let touch: AnyObject! = touches.anyObject()
		touchPoint = touch.locationInView(canvas)
	}
	
	override func touchesMoved(touches: NSSet!, withEvent event: UIEvent!) {
		// save current touch point
		let touch: AnyObject! = touches.anyObject()
		let currentPoint: CGPoint = touch.locationInView(canvas)
		
		// set canvas size to drawing area
		UIGraphicsBeginImageContext(canvas.frame.size)
		let context: CGContext! = UIGraphicsGetCurrentContext()
		
		canvas.image?.drawInRect(CGRect(x: 0, y: 0, width: canvas.frame.width, height: canvas.frame.height))
		
		// draw line in image context
		CGContextSetLineCap(context, kCGLineCapRound)
		CGContextSetLineWidth(context, 10.0)
		CGContextSetRGBStrokeColor(context, 0.0, 0.0, 0.0, 1.0)
		CGContextMoveToPoint(context, touchPoint.x, touchPoint.y)
		CGContextAddLineToPoint(context, currentPoint.x, currentPoint.y)
		CGContextStrokePath(context)
		
		// set image to canvas
		canvas.image = UIGraphicsGetImageFromCurrentImageContext()
		
		// clear graphics context
		UIGraphicsEndImageContext()
		
		touchPoint = currentPoint
	}
}

