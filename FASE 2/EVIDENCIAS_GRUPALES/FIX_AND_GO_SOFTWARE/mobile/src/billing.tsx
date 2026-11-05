/** Materiales y liquidación: los importes definitivos siempre vienen de Django. */
import { useState } from "react";
import { Linking, Text, View } from "react-native";
import { api, Page, Session } from "./api";
import type { Run } from "./screens";
import { Button, Card, Field, s } from "./ui";
import { DemoWallet } from './wallet';
import { useRefresh } from './use-refresh';
const money = (n: number) => `$${n.toLocaleString("es-CL")} CLP`;
type Extra = { id: number; description: string; quantity: number; unit_price: number; total: number; status: "PENDING" | "APPROVED" | "REJECTED" };
type Bill = { id?: number; mode?: string; webpay_enabled?: boolean; status: "DRAFT" | "PENDING" | "FAILED" | "DEMO_PAID" | "DEMO_REFUNDED"; service_amount: number; materials_amount: number; total: number; net_amount: number; vat_amount: number; vat_percent: number; commission_percent:number; commission_amount:number; provider_amount:number; has_pending_materials?: boolean; demo_enabled: boolean; snapshot: { service_description: string; materials: Extra[] }; paid_at?: string; title?: string };
type Message = { id: number; sender_id: number; text: string; created_at: string };
export type BillingData = { bill: Bill; extras: Extra[] };
// Page numbers are rebuilt locally: tokens are never sent to a next URL supplied by a server.
async function allPages<T>(path: string, token: string): Promise<T[]> {
  const rows: T[] = [];
  let number = 1;
  while (true) {
    const page = await api<Page<T>>(`${path}?page=${number}`, token);
    rows.push(...page.results);
    if (!page.next) return rows;
    number++;
    if (number > 100) throw new Error("Hay demasiados registros para esta vista del MVP.");
  }
}
export async function loadBilling(id: number, token: string): Promise<BillingData> {
  const [bill, extras] = await Promise.all([
    api<Bill>(`requests/${id}/billing/`, token),
    allPages<Extra>(`requests/${id}/materials/`, token),
  ]);
  return { bill, extras };
}
export function BillingPanel({id, session, status, data, busy, run, refresh}: {
  id: number; session: Session; status: string; data: BillingData; busy: boolean; run: Run; refresh: () => Promise<void>;
}) {
  const [description, setDescription] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [price, setPrice] = useState("");
  const [receipt, setReceipt] = useState<Bill | null>(null);
  const [messages, setMessages] = useState<Message[] | null>(null);
  const [message, setMessage] = useState("");
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [showSimulator, setShowSimulator] = useState(false);
  const {bill, extras} = data;
  const client = session.user.role === "CLIENT";
  const frozen = bill.status !== "DRAFT";
  const paid = bill.status === "DEMO_PAID";
  const refunded = bill.status === 'DEMO_REFUNDED';
  const path = `requests/${id}/`;
  const loadMessages = async () => setMessages(await allPages<Message>(`${path}messages/`, session.token));
  const chatError = useRefresh(loadMessages, paid && messages !== null, busy);
  const decide = (extra: Extra, decision: "APPROVED" | "REJECTED") => run(async () => {
    await api(`${path}materials/${extra.id}/decision/`, session.token, "POST", {decision});
    await refresh();
  });
  return <>
    <Card>
      <Text style={s.title}>Materiales adicionales</Text>
      <Text style={s.body}>Solo se incluyen en el total los materiales aprobados por el cliente. Sus precios incluyen el impuesto de demostración.</Text>
      {extras.length === 0 && <Text style={s.body}>No hay materiales adicionales.</Text>}
      {extras.map(extra => <View key={extra.id} style={{gap:8, paddingVertical:12, borderBottomWidth:1, borderColor:"#DEE5E5"}}>
        <Text style={s.label}>{extra.description}</Text>
        <Text style={s.body}>{extra.quantity} × {money(extra.unit_price)} = {money(extra.total)}</Text>
        <Text style={s.badge}>{{PENDING:"Pendiente de aprobación", APPROVED:"Aprobado", REJECTED:"Rechazado"}[extra.status]}</Text>
        {client && !frozen && extra.status === "PENDING" && <>
          <Button label={`Aprobar ${money(extra.total)}`} busy={busy} onPress={() => void decide(extra, "APPROVED")} />
          <Button secondary label="Rechazar material" busy={busy} onPress={() => void decide(extra, "REJECTED")} />
        </>}
      </View>)}
      {!client && !frozen && status === 'ACCEPTED' && <>
        <Field label="Descripción del material" value={description} maxLength={240} onChangeText={setDescription} />
        <Field label="Cantidad" keyboardType="number-pad" value={quantity} onChangeText={setQuantity} />
        <Field label="Precio unitario total en CLP" keyboardType="number-pad" value={price} onChangeText={setPrice} />
        <Button label="Proponer costo adicional" busy={busy} disabled={!description.trim() || !/^\d+$/.test(quantity) || Number(quantity)<1 || Number(quantity)>10000 || !/^\d+$/.test(price) || Number(price)<1 || Number(price)>100000000} onPress={() => void run(async () => {
          await api(`${path}materials/`, session.token, "POST", {description:description.trim(), quantity:Number(quantity), unit_price:Number(price)});
          setDescription(""); setPrice(""); setQuantity("1"); await refresh();
        })} />
      </>}
      {frozen && <Text style={s.body}>El total ya fue confirmado; los materiales están cerrados.</Text>}
    </Card>
    <Card>
      <Text style={s.title}>{paid ? 'Pago confirmado' : refunded ? 'Pago reembolsado' : 'Tu pago, sin sorpresas'}</Text>
      <View style={{backgroundColor:'#171717', borderRadius:20, padding:24, gap:8}}>
        <Text style={{color:'#D6D6D6', fontSize:15}}>Total de la demostración</Text>
        <Text accessibilityRole="header" style={{color:'#FFFFFF', fontSize:38, fontWeight:'800'}}>{money(bill.total)}</Text>
        <Text style={{color:'#FFD578', fontSize:14, fontWeight:'700'}}>MODO DE PRUEBA · SIN COBRO REAL</Text>
      </View>
      <View style={{flexDirection:'row', justifyContent:'space-between', gap:12}}><Text style={s.body}>Servicio acordado</Text><Text style={s.label}>{money(bill.service_amount)}</Text></View>
      <View style={{flexDirection:'row', justifyContent:'space-between', gap:12}}><Text style={s.body}>Materiales aprobados</Text><Text style={s.label}>{money(bill.materials_amount)}</Text></View>
      <Button secondary label={showBreakdown ? 'Ocultar desglose' : 'Ver impuestos y comisión incluidos'} onPress={() => setShowBreakdown(!showBreakdown)}/>
      {showBreakdown && <>
      <Text style={s.body}>Neto: {money(bill.net_amount)} · IVA ilustrativo incluido ({bill.vat_percent}%): {money(bill.vat_amount)}</Text>
      <Text style={s.body}>Comisión FIX&GO ({bill.commission_percent}% del servicio): {money(bill.commission_amount)}. Incluida en el precio, no se suma al cliente.</Text>
      <Text style={s.body}>Para el prestador: {money(bill.provider_amount)}, incluidos materiales. Es un desglose de demostración, no una transferencia.</Text>
      </>}
      <Text accessibilityLiveRegion="polite" style={s.badge}>{{DRAFT:"Listo para revisar", PENDING:"Esperando el pago de prueba", FAILED:"Pago no aprobado · puedes reintentar", DEMO_PAID:"Pago de prueba aprobado",DEMO_REFUNDED:'Reembolsado · demo'}[bill.status]}</Text>
      <Text style={s.body}>Dinero real que pagarás: $0. Usa solo los datos de prueba. El comprobante no es una boleta tributaria.</Text>
      {!bill.demo_enabled && !paid && <Text style={s.body}>El pago de demostración está deshabilitado en este servidor.</Text>}
      {bill.has_pending_materials && <Text style={s.body}>Resuelve los materiales pendientes antes de confirmar el total.</Text>}
      {!paid&&!refunded&&<Text style={s.body}>Acepta la cotización y resuelve los materiales. Después paga la demostración para habilitar el chat y comenzar el trabajo.</Text>}
      {client && status === "ACCEPTED" && !frozen && !bill.webpay_enabled && <Button label="Confirmar total de prueba" busy={busy} disabled={!bill.demo_enabled || bill.has_pending_materials} onPress={() => void run(async () => {
        await api(`${path}checkout/`, session.token, "POST", {}); await refresh();
      })} />}
      {client && status === 'ACCEPTED' && !paid && !refunded && bill.webpay_enabled && <>
        <Button label={bill.mode === 'WEBPAY_INT' && bill.status === 'PENDING' ? 'Continuar el pago pendiente' : `Pagar ${money(bill.total)} · de prueba`} busy={busy} disabled={bill.has_pending_materials} onPress={() => void run(async () => {
          const result = await api<{url: string}>(`${path}payment/webpay/`, session.token, 'POST', {});
          await refresh(); await Linking.openURL(result.url);
        })}/>
        <Text style={s.body}>Abriremos Webpay de prueba. Tu solicitud se actualizará automáticamente al volver a esta pestaña.</Text>
      </>}
      {client && status === 'ACCEPTED' && !paid && !refunded && bill.demo_enabled && bill.mode !== 'WEBPAY_INT' && <>
        {bill.webpay_enabled && <Button secondary label={showSimulator ? 'Ocultar simulador local' : 'Probar sin conexión con Transbank'} onPress={() => setShowSimulator(!showSimulator)}/>}
        {(!bill.webpay_enabled || showSimulator) && <>
        <DemoWallet session={session} run={run} busy={busy}/>
        <Button label={bill.status === "FAILED" ? "Reintentar demo con aprobación" : "Simular pago aprobado"} busy={busy} disabled={bill.has_pending_materials} onPress={() => void run(async () => {
          await api(`${path}checkout/`, session.token, 'POST', {});
          await api(`${path}payment/demo-result/`, session.token, "POST", {outcome:"approved"}); await refresh();
        })} />
        <Button secondary label="Simular rechazo de pago" busy={busy} disabled={bill.has_pending_materials} onPress={() => void run(async () => {
          await api(`${path}checkout/`, session.token, 'POST', {});
          await api(`${path}payment/demo-result/`, session.token, "POST", {outcome:"rejected"}); await refresh();
        })} />
        </>}
      </>}
      {(paid||refunded) && <Button secondary label="Ver comprobante de demostración" busy={busy} onPress={() => void run(async () => setReceipt(await api<Bill>(`${path}receipt/`, session.token)))} />}
      {receipt && <View style={{gap:8}}>
        <Text style={s.title}>{receipt.title}</Text>
        <Text style={s.body}>Orden #{receipt.id} · {receipt.paid_at ? new Date(receipt.paid_at).toLocaleString("es-CL") : ""}</Text>
        <Text style={s.body}>{receipt.snapshot.service_description}: {money(receipt.service_amount)}</Text>
        {receipt.snapshot.materials.map(m => <Text key={m.id} style={s.body}>{m.description} ({m.quantity}): {money(m.total)}</Text>)}
        <Text style={s.label}>Total: {money(receipt.total)} · Sin validez tributaria</Text>
      </View>}
    </Card>
    <Card>
      <Text style={s.title}>Conversación del servicio</Text>
      {!paid ? <Text style={s.body}>{refunded?'Conversación cerrada después del reembolso.':'Se habilita después de aprobar el pago de demostración.'}</Text> : <>
        <Button secondary label={messages ? "Actualizar conversación" : "Abrir conversación"} busy={busy} onPress={() => void run(loadMessages)} />
        {messages !== null && <Text style={s.body}>Los mensajes se actualizan automáticamente cada 5 segundos.</Text>}
        {!!chatError && <Text accessibilityRole="alert" style={s.body}>{chatError}</Text>}
        {messages?.length === 0 && <Text style={s.body}>Todavía no hay mensajes.</Text>}
        {messages?.map(m => <View key={m.id} style={{padding:12, borderRadius:12, backgroundColor:m.sender_id === session.user.id ? "#FFF1BD" : "#EDF2F2", gap:4}}>
          <Text style={s.label}>{m.sender_id === session.user.id ? "Tú" : client ? "Prestador" : "Cliente"} · {new Date(m.created_at).toLocaleString("es-CL")}</Text>
          <Text style={s.body}>{m.text}</Text>
        </View>)}
        <Field label="Mensaje" multiline maxLength={2000} value={message} onChangeText={setMessage} />
        <Button label="Enviar mensaje" busy={busy} disabled={!message.trim()} onPress={() => void run(async () => {
          await api(`${path}messages/`, session.token, "POST", {text:message.trim()}); setMessage(""); await loadMessages();
        })} />
      </>}
    </Card>
  </>;
}
