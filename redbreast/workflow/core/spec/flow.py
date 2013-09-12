#coding=utf8
from redbreast.workflow.core.utils import EventDispatcher, Event
from task import *

class AbstractWorkflowSpec(object):
    def __init__(self):
        super(AbstractWorkflowSpec, self).__init__()

class WorkflowSpec(AbstractWorkflowSpec, EventDispatcher):
    
    #Events
    EVENT_WF_ADDTASK = "EVENT_WF_ADDTASK"
    
    #Specail Tasks
    TASK_START = "taskStart"
    
    def __init__(self, name=None):
        super(WorkflowSpec, self).__init__()

        self.name = name or ''
        self.description = ''
        self.task_specs = dict()
        #self.dispatcher = EventDispatcher()

        self.start = StartTask(self, WorkflowSpec.TASK_START)
        
    def validate(self):
        return True
    
    def serialize(self):
        pass
    
    def deserialize(self):
        pass
    
    def get_dump(self, verbose=False):
        done = set()
    
        def recursive_dump(task_spec, indent):
            if task_spec in done:
                return  '[shown earlier] %s (%s)' % (task_spec.name, task_spec.__class__.__name__) + '\n'
    
            done.add(task_spec)
            dump = '%s (%s)' % (task_spec.name, task_spec.__class__.__name__) + '\n'
            if verbose:
                if task_spec.inputs:
                    dump += indent + '-  IN: ' + ','.join(['%s' % t.name for t in task_spec.inputs]) + '\n'
                if task_spec.outputs:
                    dump += indent + '- OUT: ' + ','.join(['%s' % t.name for t in task_spec.outputs]) + '\n'
            sub_specs = ([task_spec.spec.start] if hasattr(task_spec, 'spec') else []) + task_spec.outputs
            for i, t in enumerate(sub_specs):
                dump += indent + '   --> ' + recursive_dump(t,indent+('   |   ' if i+1 < len(sub_specs) else '       '))
            return dump
    
    
        dump = recursive_dump(self.start, '')
    
        return dump
    
    def dump(self):
        print "-------------------------------------------"
        print "Workflow: %s" % self.name
        print self.get_dump()
        print "-------------------------------------------"
        
    def on_addchild(self, task_spec):
        """
        Veto function, could be overwrote with special validation.
        """
        return True
        
    def _notify_addchild(self, task_spec):
        if task_spec.name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + task_spec.name)
        
        #veto
        if self.on_addchild(task_spec):
            self.task_specs[task_spec.name] = task_spec
            task_spec.id = len(self.task_specs)
            
            #pubsub
            event = Event(WorkflowSpec.EVENT_WF_ADDTASK, self, {"task_spec": task_spec})
            self.fire(event)
            
            