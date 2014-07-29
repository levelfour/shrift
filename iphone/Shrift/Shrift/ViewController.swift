//
//  ViewController.swift
//  Shrift
//
//  Created by Tsutsumi Fukumu on 7/27/14.
//  Copyright (c) 2014 ***. All rights reserved.
//

import UIKit

class ViewController: UIViewController {
	var toolbar: UIToolbar!
	var canvas: UIImageView!
	var touchPoint: CGPoint!
	
	override func viewDidLoad() {
		super.viewDidLoad()
		
		toolbar = UIToolbar(frame: CGRect(x: 0, y: UIApplication.sharedApplication().statusBarFrame.size.height, width: UIScreen.mainScreen().bounds.width, height: 44))
		self.view.addSubview(toolbar)
		
		canvas = UIImageView(frame: CGRect(x: 0, y: toolbar.frame.origin.y+toolbar.frame.height, width: UIScreen.mainScreen().bounds.width, height: UIScreen.mainScreen().bounds.height - toolbar.bounds.height))
		canvas.backgroundColor = UIColor.whiteColor()
		self.view.addSubview(canvas)
		
		let spaceBtn = UIBarButtonItem(barButtonSystemItem: UIBarButtonSystemItem.FlexibleSpace, target: self, action: nil)
		let trashBtn = UIBarButtonItem(barButtonSystemItem: UIBarButtonSystemItem.Trash, target: self, action: "clearCanvas")
		let cameraBtn = UIBarButtonItem(barButtonSystemItem: UIBarButtonSystemItem.Camera, target: self, action: "saveImageToAlbum")
		let actionBtn = UIBarButtonItem(barButtonSystemItem: UIBarButtonSystemItem.Action, target: self, action: "recognize")
		let items: NSMutableArray = NSMutableArray(array: [cameraBtn, actionBtn, spaceBtn, trashBtn])
		toolbar.setItems(items, animated: false)
	}

	override func didReceiveMemoryWarning() {
		super.didReceiveMemoryWarning()
		// Dispose of any resources that can be recreated.
	}
	
	func clearCanvas() {
		canvas.image = nil
	}
	
	func saveImageToAlbum() {
		UIImageWriteToSavedPhotosAlbum(canvas.image, nil, nil, nil)
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
		let url = NSURL(string: "http://tsg.ne.jp/levelfour/shrift/upload")
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
		println(filename)
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

