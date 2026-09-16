from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'build/deck_v6.mjs').read_text(encoding='utf-8')
def block(key):
    start=s.index("{\n const s=slide("+key+',') if key not in ['17'] else s.index("{\n const s=slide(17,")
    end=s.find('\n{\n',start+2)
    if end<0:end=s.index('\nconst seconds=',start)
    return s[start:end]+'\n'
first=s[:s.index("{\n const s=slide('initial_wealth',")]
first=first.replace('_v6','_v7').replace('physical>14','physical>18')
first=first.replace("Câmbio real\\ne carry trade","Câmbio real, termos de troca\\ne carry trade")
first=first.replace("1152,104,42","1152,104,39")
first=first.replace("1130,180,64","1130,180,58")
new=(R/'build/new_slides_v7.mjs').read_text(encoding='utf-8')
backup='\n'.join(block(k) for k in ['10','11','12',"'tenure'",'17'])
backup=backup.replace("['Carry','Carry por juros',navy],['Equal_modules','Combinação',teal]","['Carry','Carry por juros',pal.Carry],['Equal_modules','Combinação',pal.Matched]")
backup=backup.replace('ao slide anterior','ao resultado da combinação')
tail=s[s.index('const seconds='):].replace('_v6','_v7').replace('mainSlides:14,backupSlides:2','mainSlides:18,backupSlides:7')
tail=tail.replace("fontPolicy:{basis:'design',families:[F]}","fontPolicy:{basis:'design',families:[F]}")
# Filename override allows corrections without overwriting a finalized revision.
tail=tail.replace("const final=path.join(root,'output/presentation/apresentacao_macro_aula_v7_final.pptx');","const tag=process.env.REVISION_TAG??'v7';\nconst final=path.join(root,`output/presentation/apresentacao_macro_aula_${tag}_final.pptx`);")
tail=tail.replace("'presentation/build/validation_v7_final.json'","`presentation/build/validation_${tag}_final.json`")
(R/'build/deck_v7.mjs').write_text(first+new+'\n'+backup+tail,encoding='utf-8')
print('Built native slide source')
