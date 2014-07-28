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
		let cameraBtn = UIBarButtonItem(barButtonSystemItem: UIBarButtonSystemItem.Camera, target: self, action: "saveImage")
		let items: NSMutableArray = NSMutableArray(array: [cameraBtn, spaceBtn, trashBtn])
		toolbar.setItems(items, animated: false)
	}

	override func didReceiveMemoryWarning() {
		super.didReceiveMemoryWarning()
		// Dispose of any resources that can be recreated.
	}
	
	func clearCanvas() {
		canvas.image = nil
	}
	
	func saveImage() {
		UIImageWriteToSavedPhotosAlbum(canvas.image, nil, nil, nil)
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

