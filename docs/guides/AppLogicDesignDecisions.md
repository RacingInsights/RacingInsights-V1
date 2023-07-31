## Notes on update methods for overlays
There are (currently) 3 use cases when an overlay needs to be updated:
1. Values changed from telemetry 
2. Appearance setting for currently available element is changed (configured)
3. A visual element is activated/deactivated and the elements need to be reloaded

The following methods are providing these as follows:

update_values(): 1

update_visuals(): 2,3 

This creates overhead and unclear code as update_visuals is used for different 2 thing at the same time.

New methods to achieve separation of functionality, each use case has 1 associated methods in the corresponding overlay classes:

1. update_telemetry_values() -> needs to set new value(s) for stringvar(s)
2. update_appearance()       -> needs to configure() tk/custom elements and update() 
3. reconstruct_overlay()     -> needs to destroy the current overlay_frame instance and rebuild it for current activated elements

renaming:
tm -> telemetry
entry_widgets -> relative_entries

update_entry -> update_telemetry_values


## Explanation for the need of queue
Currently, the user interaction of clicking a settingscheckbutton in the settings menu, triggers the reconstruct overlay method.
This method deletes all the elements of the overlay frame and then reconstructs it. Howewer, as can be seen in the image below,
this can happen while the relative_app.update_telemetry_values() is happening, for example updating all labels in the overlay.
As these labels can be deleted by the async input of the user, the program might crash in an implementation that doesn't enforce the update_telemetry_values() to finish before reconstructing.
Solution: Will implement a Queue. This way, when the user presses a button, it will add an event to the queue instead of immediately doing the process related to the button.
After completion of the current update_telemetry_values(), the event related to the button will be processed first before updating telemetry values again

<div align="center">
  <a href="">
    <img src="docs/guides/screenshots/Need_Queue_Example.png" width="500" height=auto>
  </a>
</div>

Results after implementing a queue.
<div align="center">
  <a href="">
    <img src="docs/guides/screenshots/Queue_Implementation_Result.png" width="500" height="auto">
  </a>
</div>