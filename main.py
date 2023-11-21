from loki import (
    Sourcefile, FindNodes, CallStatement, 
    Transformer, Dimension, ir, 
    Scalar, Assignment, fgen,
    FindVariables, symbols, demote_variables,
    Intrinsic, Variable, SymbolAttributes,
    DerivedType, VariableDeclaration, flatten,
    BasicType, FindInlineCalls, SubstituteExpressions,
    Nullify
)

from loki.transform import resolve_associates

import os
import sys

from termcolor import colored
import logical
import ResolveVector
import ExplicitArraySyntaxes

import re

from pathlib import Path

def load_subroutine(path, file, name):
    source=Sourcefile.from_file(path+file)
    return(source[name])

def save_subroutine(path, file):
    from pathlib import Path
    Sourcefile.to_file(fgen(routine), Path(path+name+'.F90'))


#*********************************************************
#*********************************************************
#*********************************************************
#       Some  routines  of  the  transformation
#*********************************************************
#*********************************************************
#*********************************************************


#def add_openacc1(routine):
#    call_lst=[]
#    call_map={}
#    suffix='_OPENACC'
#    stack_argument=Variable(name="YDSTACK", type=SymbolAttributes(DerivedType(name="STACK"), intent='in'))
#    stack_local=Variable(name="YLSTACK", type=SymbolAttributes(DerivedType(name="STACK")), scope=routine)
#
#    for call in FindNodes(CallStatement).visit(routine.body):
#        if call.name == "ABOR1":
#    #        call_lst.append(call.name.name) don't add in call_lst, no #include abor1_acc
#            new_call=call.clone(name=call.name, arguments=call.arguments)
#            new_call._update(name=call.name.clone(name=call.name+"_ACC"))
#            call_map.update({call : new_call})
#        elif call.name != "DR_HOOK":
#            call_lst.append(call.name.name)
#            new_call=call.clone(name=call.name, arguments=call.arguments)
#            new_call._update(name=call.name.clone(name=f'{call.name}{suffix}'))
#            new_call._update(kwarguments=new_call.kwarguments + ((stack_argument.name, stack_local),))
#            call_map.update({call : new_call})
#
#    routine_importSPEC=FindNodes(ir.Import).visit(routine.spec)
#    imp_map={}
#    for imp in routine_importSPEC:
#        name=imp.module.replace(".intfb.h","").upper()
#        if imp.c_import==True and any(call==name for call in call_lst):
#            new_name=imp.module.replace("intfb.f","")+"_openacc"+".intfb.h"
#            new_imp=imp.clone(module=new_name)
#            imp_map.update({imp : new_imp})
#    routine.body=Transformer(call_map).visit(routine.body)
#    routine.spec=Transformer(imp_map).visit(routine.spec)


def add_openacc2(routine):
    call_lst=[]
    suffix='_OPENACC'
    stack_argument=Variable(name="YDSTACK", type=SymbolAttributes(DerivedType(name="STACK"), intent='in'))
    stack_local=Variable(name="YLSTACK", type=SymbolAttributes(DerivedType(name="STACK")), scope=routine)
    for call in FindNodes(CallStatement).visit(routine.body):
        if call.name == "ABOR1":
            
        #call_lst.append(call.name.name)
            call.name.name=call.name.name+"_ACC"
#            call._update(kwarguments=call.kwarguments + ((stack_argument.name, stack_local),))

        elif call.name != "DR_HOOK":
            call_lst.append(call.name.name)
            call.name.name=call.name.name+suffix
            call._update(kwarguments=call.kwarguments + ((stack_argument.name, stack_local),))

    routine_importSPEC=FindNodes(ir.Import).visit(routine.spec)
    for imp in routine_importSPEC:
        name=imp.module.replace(".intfb.h","").upper()
        if imp.c_import==True and any(call==name for call in call_lst):
 #       # if any(call==name for call in call_lst):
 #            print("imp.module=",imp.module)
 #            print("imp.module.type=",type(imp.module))

            new_name=imp.module.replace(".intfb.h","")+"_openacc"+".intfb.h"
            imp._update(module=f'{new_name}')

def remove_loop(routine, lst_horizontal_idx):
    loop_map={}
    for loop in FindNodes(ir.Loop).visit(routine.body):
        if loop.variable in lst_horizontal_idx:
            loop_map[loop]=loop.body
    routine.body=Transformer(loop_map).visit(routine.body)

def rename(routine):
    routine.name=routine.name+'_OPENACC'

def acc_seq(routine):
    routine.spec.insert(0,ir.Pragma(keyword='acc', content='routine ('+routine.name+') seq'))
    routine.spec.insert(1,ir.Comment(text=''))

def jlon_kidia(routine, end_index, begin_index, new_range, horizontal_idx):
    
    routine.spec.append(Assignment(horizontal_idx, begin_index))
#    kidia=Scalar(begin_index)
#    routine.spec.append(Assignment(jlon, kidia))

def stack_mod(routine):
    idx=-1
    for spec in routine.spec.body:
#        if type(spec)==ir.Intrinsic and spec.text=='IMPLICIT NONE':
#            break
        if type(spec)==ir.VariableDeclaration:
            break
        idx=idx+1
    routine.spec.insert(idx-1, ir.Import(module='STACK_MOD'))
    routine.spec.insert(idx, ir.Import(module='stack.h', c_import=True))
    routine.spec.insert(idx+1, ir.Comment(text=''))

def rm_KLON(routine, horizontal, horizontal_size):
#    if horizontal_size!=horizontal.size:
#        print(colored("PB with HOR_DIM","red"))
#        print("horizontal=",horizontal.size)
#        print("horizontal_size=",horizontal_size)
#
    demote_arg=False #rm KLON in function arg if True
    routine_arg=[var.name for var in routine.arguments]
    to_demote=FindVariables(unique=True).visit(routine.spec)
    to_demote=[var for var in to_demote if isinstance(var, symbols.Array)]
    to_demote=[var for var in to_demote if var.shape[-1] == horizontal_size]
    if not demote_arg :
        to_demote = [var for var in to_demote if var.name not in routine_arg]


        calls = FindNodes(ir.CallStatement).visit(routine.body)
        call_args = flatten(call.arguments for call in calls)
        call_args += flatten(list(dict(call.kwarguments).values()) for call in calls)
        to_demote = [v for v in to_demote if v.name not in call_args]

    var_names=tuple(var.name for var in to_demote)
    #TODO demote over all horizontal dimensions if more than one
    if var_names:
        demote_variables(routine, var_names, dimensions=horizontal_size)

def alloc_temp(routine):
    routine_arg=[var.name for var in routine.arguments]
    

    temp_map={}
    for decls in FindNodes(VariableDeclaration).visit(routine.spec):
        intrinsic_lst=[] #intrinsic lst for temp macro var decl
        var_lst=[] #var to keep in the decl.
        for s in decls.symbols:
            if isinstance(s, symbols.Array):
                if not s.type.pointer:
                    if s.name not in routine_arg:
                        if s.type.kind:
                            new_s='temp ('+s.type.dtype.name+' (KIND='+s.type.kind.name+'), '+s.name+', ('
                        else:
                            new_s='temp ('+s.type.dtype.name+', '+s.name+', ('
                        for shape in s.shape:
                            new_s=new_s+str(shape)+', '
                        new_s=new_s[:-2]
                        new_s=new_s+'))'
                        alloc='alloc ('+s.name+')'
                        routine.spec.append(Intrinsic(alloc))
                        intrinsic_lst.append(Intrinsic(new_s))
                    else: #if array in routine args
#                        var_lst.append(decls.clone(symbols=s))
                        var_lst=[s]
                        VAR=decls.clone(symbols=var_lst)
                        intrinsic_lst.append(VAR)
                else: #if s is a pointer
                    #print(colored("POINTER","red"))
                    var_lst=[s]
                    VAR=decls.clone(symbols=var_lst)
                    intrinsic_lst.append(VAR)
            else: #if not an array
#                var_lst.append(decls.clone(symbols=s))
                var_lst=[s]
                VAR=decls.clone(symbols=var_lst)
                intrinsic_lst.append(VAR)

        temp_map[decls]=tuple(intrinsic_lst)
#        VAR=decls.clone(symbols=var_lst)
#        intrinsic_lst.append(VAR)

    routine.spec=Transformer(temp_map).visit(routine.spec)
    

def get_horizontal_size(routine, horizontal, lst_horizontal_size):
    verbose=False
    #verbose=True
    for name in lst_horizontal_size:
        if name in routine.variable_map:
            if verbose: print("horizontal size = ",name)
            return(name)
    for var in FindVariables().visit(routine.body):
        for vvar in var.name.split("%"):
            if vvar in lst_horizontal_size:
                if verbose: print("horizontal size = ",name)
                return(var.name)
    if verbose: print(colored("Horizontal size not found in routine args!", "red"))
#    if verbose: print("horizontal size = ", horizontal.size)
    
    
    #TODO : ajouter identification lorsque la dimension horizontale est dans un type dérivé. 
    hor_lst=[]
    var_lst=FindVariables(unique=True).visit(routine.spec)
    var_lst=[var for var in var_lst if isinstance(var, symbols.Array)]
    for var in var_lst:
        for shape in var.shape: 
            if shape in lst_horizontal_size: 
                if shape not in hor_lst:
                    hor_lst.append(shape)
    if len(hor_lst)>1:
        print(colored("diff horizontal size are used", "red"))
        return(horizontal.size)
    else:
        return(hor_lst[0])


def ystack1(routine):
#    stack_argument=Variable(name="YDSTACK", type=SymbolAttributes(DerivedType(name="STACK")),scope=routine)
    stack_argument=Variable(name="YDSTACK", type=SymbolAttributes(DerivedType(name="STACK"), intent='in'))
    stack_local=Variable(name="YLSTACK", type=SymbolAttributes(DerivedType(name="STACK")), scope=routine)

    routine.arguments+=(stack_argument,)

def ystack2(routine):
#    stack_argument=Variable(name="YDSTACK", type=SymbolAttributes(DerivedType(name="STACK")),scope=routine)
    stack_argument=Variable(name="YDSTACK", type=SymbolAttributes(DerivedType(name="STACK"), intent='in'))
    stack_local=Variable(name="YLSTACK", type=SymbolAttributes(DerivedType(name="STACK")), scope=routine)

    routine.variables+=(stack_argument, stack_local,)
    routine.spec.append(Assignment(stack_local, stack_argument))


def get_horizontal_idx(routine, lst_horizontal_idx):
    is_present=False
    verbose=False
    var_lst=FindVariables(unique=True).visit(routine.spec)
    for var in var_lst:
        if var.name=="JLON":
            is_present=True
            loop_index=var
    
    if not is_present:
        jlon=Variable(name="JLON", type=SymbolAttributes(BasicType.INTEGER, kind=Variable(name='    JPIM')))
        loop_index=jlon
        routine.variables+=(jlon,)

    loop_map={}
    for loop in FindNodes(ir.Loop).visit(routine.body):
        if loop.variable in lst_horizontal_idx:
            #new_loop=loop.clone(variable=routine.variable_map["JLON"])
            if verbose: print("loop_idx=",loop_index)
            new_loop=loop.clone(variable=routine.variable_map[loop_index.name])
            var_map={}
            for var in FindVariables().visit(loop.body):
                if (var==loop.variable):
                    var_map[var]=routine.variable_map[loop_index.name]
            loop_map[loop]=SubstituteExpressions(var_map).visit(loop.body)
            #loop.body=SubstituteExpressions(var_map).visit(loop.body)
    #        loop.variable=routine.variable_map[loop_index.name]

    routine.body=Transformer(loop_map).visit(routine.body)

    return(loop_index)


def rm_sum(routine):
    call_map={}
    for assign in FindNodes(Assignment).visit(routine.body):
        for call in FindInlineCalls().visit(assign):
            if (call.name=="SUM"):
                call_map[call]=call.parameters[0]
    if call_map:
        routine.body=SubstituteExpressions(call_map).visit(routine.body)

def generate_interface(routine, pathw):
    removal_map={}
    imports = FindNodes(ir.Import).visit(routine.spec)
    routine_new=routine.clone()
    for im in imports:
        if im.c_import==True:
            removal_map[im]=None
    routine_new.spec = Transformer(removal_map).visit(routine_new.spec)
    Sourcefile.to_file(fgen(routine_new.interface), Path(pathw+".intfb.h"))

def write_print(routine):
    verbose=False
    intr_map={}
    for intr in FindNodes(Intrinsic).visit(routine.body):
        if "WRITE" in intr.text:
            if verbose : print(colored("WRITE found in routine","red"))
            pattern='WRITE\(NULERR, \*\)(.*)'
            match=re.search(pattern,intr.text)
            string=match.group(1)
            new_intr='PRINT *, '+string
            intr_map[intr]=Intrinsic(new_intr)
    routine.body=Transformer(intr_map).visit(routine.body)
            
    
#---------------------------------------------------------
#---------------------------------------------------------
#Pointers
#---------------------------------------------------------
#---------------------------------------------------------

def find_pt(routine):
    tmp_pt=[]
    tmp_target=[]
    #for var in FindVariables().visit(routine.variables):
    routine_args=[var.name for var in routine.arguments]
    for decls in FindNodes(VariableDeclaration).visit(routine.spec):
        for s in decls.symbols:
            if s.name not in routine_args:
                if s.type.pointer:
                    tmp_pt.append(s)
            if s.type.target:
                tmp_target.append(s)
    return(tmp_pt, tmp_target)
             
             
def get_dim_pt(routine, tmp_pt, tmp_target, horizontal_size):
    assign_map={}
    tmp_pt_klon={}
    for assign in FindNodes(Assignment).visit(routine.body):
        assigned=False
        is_target=False
        is_pt=False
        rhs=FindVariables().visit(assign.rhs)
        rhs=list(rhs)
        lhs=FindVariables().visit(assign.lhs)
        lhs=list(lhs)
        if (len(rhs)==1 and len(lhs)==1):
            for pt in tmp_pt:
                if pt.name==lhs[0].name:
                   is_pt=True
                   break
            for target in tmp_target:
                if target.name==rhs[0].name:
                   is_target=True
                   break
            if is_pt and is_target:
                if target.dimensions[0]=='KPROMA': #replace KPROMA by hor_dim... here we assume that if they are no dim, then the dim isn't NPROMA.... 
                    tmp_pt_klon[lhs[0].name]=rhs[0]
                    new_assign='assoc ('+lhs[0].name+','+rhs[0].name+')'
                    assign_map[assign]=Intrinsic(new_assign)
                    assigned=True
        if not assigned:
            assign_map[assign]=assign
    routine.body=Transformer(assign_map).visit(routine.body) 
    #TODO ::: MAPING MODIFIER LES A => B en assoc(A,B)
    return(tmp_pt_klon)

def nullify(routine, tmp_pt_klon):
#    null=FindNodes(Nullify).visit(routine.body)
    null_map={}
    for null in FindNodes(Nullify).visit(routine.body):
        new_null=()
        for pt in null.variables:
            if null.variables[0].name in tmp_pt_klon:
                new_intr=Intrinsic("nullptr("+null.variables[0].name+")")
                new_null=new_null+(new_intr,)
        null_map[null]=new_null
    routine.body=Transformer(null_map).visit(routine.body)
#define target lst to avoid A.type => bug



def assoc_alloc_pt(routine, tmp_pt_klon):
    temp_map={}
    for decls in FindNodes(VariableDeclaration).visit(routine.spec):
        intrinsic_lst=[]
        var_lst=[]
        for s in decls.symbols:
            if s.name in tmp_pt_klon:
                var=tmp_pt_klon[s.name]
                if var.type.kind:
                    new_s='temp ('+var.type.dtype.name+' (KIND='+var.type.kind.name+'), '+s.name+', ('
                else:
                    new_s='temp ('+var.type.dtype.name+', '+s.name+', ('
                for shape in var.shape:
                    new_s=new_s+str(shape)+', '
                new_s=new_s[:-2]
                new_s=new_s+'))'
                #alloc='alloc ('+s.name+')'
                #routine.spec.append(Intrinsic(alloc))
                intrinsic_lst.append(Intrinsic(new_s))
            else:
                var_lst=[s]
                VAR=decls.clone(symbols=var_lst)
                intrinsic_lst.append(VAR)
        temp_map[decls]=tuple(intrinsic_lst)
    routine.spec=Transformer(temp_map).visit(routine.spec)
#def add_contains():
#    with open('callee.F90', 'r') as file_callee:
#        callee = file_callee.read()
#    with open('caller.F90', 'r') as file_caller:
#        caller = file_caller.read()
#
#    string="END SUBROUTINE"
#    loc=caller.find(string)
#    callee="CONTAINS\n\n"+callee
#    if loc != -1:
#        new_caller=caller[:loc]+callee+caller[loc:]
#    with open('caller.F90', 'w') as file_caller:
#        file_caller.write(new_caller)

#*********************************************************
#*********************************************************
#*********************************************************
#      Functions    needed    for    inlining....
#*********************************************************
#*********************************************************
#*********************************************************

#def inline_calls(inlined):
def inline_calls(pathpack, pathview, pathfile, pathacc, horizontal_opt, inlined):
    verbose=True
    pathr=pathpack+'/'+pathview+pathfile
    match_inline=False
#    for routine_name in 
#    if routine_name=
#    for call in FindNodes(CallStatement).visit(routine.body):
#        if call.name in inlined:
#            add_contains
    dict_callee_path={}
    if inlined != None:    
           
   
        with open('/home/gmap/mrpm/cossevine/build_scc/openacc49.sh', 'r') as file_lst_callee:
            lines=file_lst_callee.readlines()
            for callee_name in inlined:
                callee_path=None
                for line in lines:
                    callee_path=re.search('((\w*\/)+'+callee_name+')', line)
                    if callee_path:
                        
                        callee_path=pathpack+'/'+pathview+callee_path.group(0)
                        dict_callee_path[callee_name]=callee_path
        if verbose: print("dict_callee_path=",dict_callee_path)

        with open(pathr, 'r') as file_caller:
            caller = file_caller.read()

	#new_caller=caller
        for callee_name in inlined: #look for each callee sub  in the caller
            if caller.find(callee_name.replace(".F90","").upper())!=-1:
                with open(dict_callee_path[callee_name], 'r') as file_callee:
                    callee = file_callee.read()
                if not match_inline: #add CONTAINS only for the first callee matching
                    match_inline=True
                    callee="CONTAINS\n\n"+callee
                    loc=caller.find("END SUBROUTINE")
                    if loc != -1 :
                        caller=caller[:loc]+callee+caller[loc:]
                else: #add the callee after the CONTAINS statement
                    loc=caller.find("CONTAINS")
                    if loc != -1 :
                         loc=loc+len("CONTAINS\n\n") #insert after CONTAINS
                         caller=caller[:loc]+callee+caller[loc:]
        if verbose: print(pathpack+"/tmp/"+os.path.basename(pathfile))
        if match_inline:
            with open(pathpack+"/tmp/"+os.path.basename(pathfile), "w") as file_caller:
                file_caller.write(caller)
    else:
        if verbose: print(colored("no routine to inline", "red"))


    return(match_inline)

#diff way to do : uniformize loop or re.search(_LOOPIDX) 
def rename_hor(routine, lst_horizontal_idx): 
#    lst_horizontal_idx_new
#    for idx in lst_horizontal_idx:
#    
#        lst_horizontal_idx_new=lst_horizontal_idx_new+
    rename_map={}
    for var in FindVariables().visit(routine.body):
        for idx in lst_horizontal_idx:
            if '_'+idx in var.name:
                rename_map[var]=var.clone(name=idx.replace("_",""))
    routine.body=SubstituteExpressions(rename_map).visit(routine.body)
                    
     
#*********************************************************
#*********************************************************
#*********************************************************
#       Defining     the       transformation
#*********************************************************
#*********************************************************
#*********************************************************

import click

@click.command()
#@click.option('--pathr', help='path of the file to open')
#@click.option('--pathw', help='path of the file to write to')
@click.option('--pathpack', help='path to the pack')
@click.option('--pathview', help='path to src/local or whatever..')
@click.option('--pathfile', help='path to the file')
@click.option('--pathacc', help='path to the place acc files are stored')

@click.option('--horizontal_opt', default=None, help='some hor opt... for now an additionnal possible horizontal idx')
@click.option('--inlined', '-in', default=None, multiple=True, help='names of the routine to inline')

def openacc_trans(pathpack, pathview, pathfile, pathacc, horizontal_opt, inlined):

    #setup

    verbose=True
    #verbose=False
    pathr=pathpack+'/'+pathview+pathfile
    pathw=pathpack+pathacc+'/'+pathfile

    pathw=pathw.replace(".F90", "")+"_openacc"
    
    print(pathr)
    print(pathw)

    import logical_lst
    
    horizontal=Dimension(name='horizontal',size='KLON',index='JLON',bounds=['KIDIA','KFDIA'],aliases=['NPROMA','KDIM%KLON','D%INIT'])
    vertical=Dimension(name='vertical',size='KLEV',index='JLEV')
    
     #lst_horizontal_idx=['JLON','JROF','JL']
    lst_horizontal_idx=['JLON','JROF']
    #the JL idx have to be added only when it's used at an horizontal idx, because it's used as avertical idx in some places.... this should be fixed... The transformation script could check wether JL is a hor or vert idx instead of adding JL to the lst_horizontal_idx conditionally. 
    if horizontal_opt is not None:
        lst_horizontal_idx.append(horizontal_opt)
    if verbose: print("lst_horizontal_idx=",lst_horizontal_idx)
    
    lst_horizontal_size=["KLON","YDCPG_OPTS%KLON","YDGEOMETRY%YRDIM%NPROMA","KPROMA", "YDDIM%NPROMA", "NPROMA"]
    lst_horizontal_bounds=[["KIDIA", "YDCPG_BNDS%KIDIA","KST"],["KFDIA", "YDCPG_BNDS%KFDIA","KEND"]]
    
    true_symbols, false_symbols=logical_lst.symbols()
    false_symbols.append('LHOOK')
    
    #inlining : 
    inline_match=inline_calls(pathpack, pathview, pathfile, pathacc, horizontal_opt, inlined)
    if inline_match:
        filename=os.path.basename(pathfile)
        source=Sourcefile.from_file(pathpack+"/tmp/"+filename)
    else:
        source=Sourcefile.from_file(pathr)
    routine=source.subroutines[0]

    from loki.transform import inline_member_procedures
    
    if inline_match:
        routine.enrich_calls(routine.members)
        inline_member_procedures(routine)
        rename_hor(routine, lst_horizontal_idx)

    #transformations:
    horizontal_size=get_horizontal_size(routine, horizontal, lst_horizontal_size)
    resolve_associates(routine)
    logical.transform_subroutine(routine, true_symbols, false_symbols)
    
    end_index, begin_index, new_range=ExplicitArraySyntaxes.ExplicitArraySyntaxes(routine, lst_horizontal_size, lst_horizontal_bounds)
    horizontal_idx=get_horizontal_idx(routine, lst_horizontal_idx)
    bounds=[begin_index, end_index]
    add_openacc2(routine)
    
    rename(routine)
    acc_seq(routine)
    stack_mod(routine)
    rm_KLON(routine, horizontal, horizontal_size)
    ResolveVector.resolve_vector_dimension(routine, horizontal_idx, bounds)
    
    remove_loop(routine, lst_horizontal_idx)
    ###
    ystack1(routine)
    rm_sum(routine)
    generate_interface(routine, pathw) #must be before temp allocation and y stack, or temp will be in interface
    
    ##----------------------------------------
    ##Pointers
    ##----------------------------------------
    tmp_pt, tmp_target=find_pt(routine)
    tmp_pt_klon=get_dim_pt(routine, tmp_pt, tmp_target, horizontal_size)
    assoc_alloc_pt(routine, tmp_pt_klon)
    nullify(routine, tmp_pt_klon)
    ##----------------------------------------
    ##----------------------------------------
    write_print(routine)
    
    ystack2(routine)
    alloc_temp(routine)
    jlon_kidia(routine, end_index, begin_index, new_range, horizontal_idx) #at the end
    
    
    Sourcefile.to_file(fgen(routine), Path(pathw+".F90"))
#    Sourcefile.to_file(fgen(routine), Path(pathW.replace(".F90", "")+"_openacc"+".F90"))

#*********************************************************
#*********************************************************
#*********************************************************
#            TESTING     INLINE 
#*********************************************************
#*********************************************************
#*********************************************************

#def openacc_trans(pathpack, pathview, pathfile, pathacc, horizontal_opt, inlined):
#    print("inlined=",inlined)
#    pathr=pathpack+pathview+pathfile
#    pathw=pathpack+pathacc+pathfile
#    
#    pathw=pathw.replace(".F90", "")+"_openacc"
#    
#    match=inline_calls(pathpack, pathview, pathfile, pathacc, horizontal_opt, inlined)
#
#*********************************************************
#*********************************************************
#*********************************************************
#       Calling  the       transformation
#*********************************************************
#*********************************************************
#*********************************************************

openacc_trans()
#openacc_trans(pathpack, pathview, pathfile, pathacc, horizontal_opt, inlined)

