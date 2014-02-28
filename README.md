PySwarm
=======

This is a Python script for use with Autodesk Maya.  It's a crowd system tool with a fully featured UI that artists can use to create bug swarms, migrating animals and so on within their scene.  I've added a few extra twists inspired by scenes from recent movies too. ;)

It's still a work in progress at this current point in time, I'll be adding a full set of instructions, along with open source licence, technical notes & so on once it's all finished.  
In a nutshell though, I've always been kind of interested in emergent behaviours and was thinking of creating a swarm scene or something in Maya, but then I noticed there aren't really any readily available tools for doing so.  Only one I came across was Carsten Kolve's "BrainBugz" plugin.  Which is a nice piece of work, of course, but it's a C++ plugin written back in 2006 - good luck getting that compiled & playing nicely with Maya 2014.  
What I'm aiming to make here is a nice plug'n'play, cross-platform crowd system tool that will just work.  And not just a quick & dirty "boids" implementation that works in some contrived situation, but a proper pipeline tool that artists might actually want to use.  
It's also an opportunity to become more familiar with Python and developing for Maya, both of which are relatively new to me.  

So far I've just implemented it as a straight script, using Pymel to interact with the Maya, rather than as a full-blown plugin simply because there's been no real need to use the Maya API just yet, although that might change at some point we'll see how it goes.
Anyway, it's going OK so far, still got some work to do but it's getting there; & when it is there I'll also get round to writing a proper doc.

thanks for looking.
