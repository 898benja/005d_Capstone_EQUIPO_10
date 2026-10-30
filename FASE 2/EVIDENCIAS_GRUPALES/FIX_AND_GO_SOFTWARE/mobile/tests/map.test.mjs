import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import ts from 'typescript';
const source=readFileSync(new URL('../src/map-contract.ts',import.meta.url),'utf8');
const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext}}).outputText;
const {validPoint,handleMapMessage}=await import(`data:text/javascript;base64,${Buffer.from(js).toString('base64')}`);
test('rechaza coordenadas inválidas y acepta Santiago',()=>{
  for(const p of [null,{}, {latitude:NaN,longitude:-70.6},{latitude:-33.4,longitude:Infinity},{latitude:0,longitude:0},{latitude:'-33.4',longitude:-70.6}])assert.equal(validPoint(p),false);
  assert.equal(validPoint({latitude:-33.45,longitude:-70.67}),true);
});
test('mensajes inválidos y prestadores desconocidos no activan navegación',()=>{
  let calls=0;
  const props={markers:[{id:3}],onPoint:()=>calls++,onSelect:()=>calls++};
  for(const raw of ['invalid','{}','null',JSON.stringify({source:'evil',type:'provider',id:3}),JSON.stringify({source:'fixgo-map',type:'provider',id:4})])handleMapMessage(raw,props);
  assert.equal(calls,0);
  handleMapMessage({source:'fixgo-map',type:'provider',id:3},props);
  handleMapMessage({source:'fixgo-map',type:'point',point:{latitude:-33.45,longitude:-70.67}},props);
  assert.equal(calls,2);
});
