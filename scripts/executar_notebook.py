import json
import argparse
from pathlib import Path
from jupyter_client import KernelManager
parser=argparse.ArgumentParser(description='Executa um notebook em kernel novo e salva as saídas.')
parser.add_argument('notebook', type=Path)
p=parser.parse_args().notebook.resolve()
nb=json.loads(p.read_text(encoding='utf-8'))
km=KernelManager(kernel_name='enem-2025')
km.start_kernel(cwd=str(p.parent))
kc=km.client()
kc.start_channels()
try:
    kc.wait_for_ready(timeout=60)
    for i,c in enumerate(nb['cells']):
        if c['cell_type']!='code': continue
        print(f'Executando celula {i}',flush=True)
        c['outputs']=[]
        def registrar(msg):
            t=msg['header']['msg_type']; content=msg['content']
            if t=='stream': c['outputs'].append({'output_type':'stream','name':content['name'],'text':content['text']})
            elif t in ('display_data','execute_result'):
                out={'output_type':t,'data':content['data'],'metadata':content['metadata']}
                if t=='execute_result': out['execution_count']=content['execution_count']
                c['outputs'].append(out)
            elif t=='error': c['outputs'].append({'output_type':'error',**content})
        reply=kc.execute_interactive(''.join(c['source']),timeout=1800,output_hook=registrar)
        c['execution_count']=reply['content'].get('execution_count')
        p.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf-8')
        if reply['content']['status']!='ok': raise RuntimeError(reply['content'])
        print(f'Celula {i}: OK',flush=True)
    print('Notebook completo: OK',flush=True)
finally:
    kc.stop_channels(); km.shutdown_kernel(now=True)
