import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import ts from 'typescript';
const source = readFileSync(new URL('../src/service-progress.ts', import.meta.url), 'utf8');
const js = ts.transpileModule(source, {compilerOptions:{module:ts.ModuleKind.ESNext}}).outputText;
const {serviceProgress} = await import(`data:text/javascript;base64,${Buffer.from(js).toString('base64')}`);
test('el siguiente paso depende de pago confirmado, no solo cotización aceptada', () => {
  assert.equal(serviceProgress('ACCEPTED','FAILED',true).step,3);
  assert.equal(serviceProgress('ACCEPTED','PENDING',false).step,3);
  assert.equal(serviceProgress('ACCEPTED','DEMO_PAID',true).step,4);
});
test('el reembolso domina el estado antiguo del trabajo', () => {
  assert.equal(serviceProgress('IN_PROGRESS','DEMO_REFUNDED',true).title,'Pago reembolsado');
  assert.equal(serviceProgress('CANCELLED',undefined,true).step,0);
});
