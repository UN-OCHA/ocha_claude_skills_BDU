import AppKit
for p in CommandLine.arguments.dropFirst() {
  guard let img = NSImage(contentsOf: URL(fileURLWithPath: p)) else { print("fail", p); continue }
  let w = Int(img.size.width), h = Int(img.size.height), k = 4
  let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w*k, pixelsHigh: h*k, bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
  NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
  NSColor.white.set(); NSRect(x:0,y:0,width:w*k,height:h*k).fill()
  img.draw(in: NSRect(x:0,y:0,width:w*k,height:h*k)); NSGraphicsContext.restoreGraphicsState()
  var minY = Int.max, maxY = -1, minX = Int.max, maxX = -1
  for y in 0..<(h*k) { for x in stride(from:0, to:w*k, by:1) { let c = rep.colorAt(x:x,y:y)!; if c.redComponent < 0.95 || c.greenComponent < 0.95 || c.blueComponent < 0.95 { minY=min(minY,y); maxY=max(maxY,y); minX=min(minX,x); maxX=max(maxX,x) } } }
  print(String(format:"%@: %dx%d ink x %.1f-%.1f y %.1f-%.1f", (p as NSString).lastPathComponent, w, h, Double(minX)/Double(k), Double(maxX+1)/Double(k), Double(minY)/Double(k), Double(maxY+1)/Double(k)))
}
