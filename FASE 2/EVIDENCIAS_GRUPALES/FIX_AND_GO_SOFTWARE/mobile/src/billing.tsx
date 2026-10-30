/** Materiales y liquidación: los importes definitivos siempre vienen de Django. */
import { useState } from "react";
import { Text, View } from "react-native";
import { api, Page, Session } from "./api";
import type { Run } from "./screens";
import { Button, Card, Field, s } from "./ui";
import { DemoWallet } from './wallet';
const money = (n: number) => `$${n.toLocaleString("es-CL")} CLP`;
type Extra = { id: number; description: string; quantity: number; unit_price: number; total: number; status: "PENDING" | "APPROVED" | "REJECTED" };
type Bill = { id?: number; status: "DRAFT" | "PENDING" | "FAILED" | "DEMO_PAID" | "DEMO_REFUNDED"; service_amount: number; materials_amount: number; total: number; net_amount: number; vat_amount: number; vat_percent: number; commission_percent:number; commission_amount:number; provider_amount:number; has_pending_materials?: boolean; demo_enabled: boolean; snapshot: { service_description: string; materials: Extra[] }; paid_at?: string; title?: string };
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
  const {bill, extras} = data;
  const client = session.user.role === "CLIENT";
  const frozen = bill.status !== "DRAFT";
  const paid = bill.status === "DEMO_PAID";
  const refunded = bill.status === 'DEMO_REFUNDED';
  const path = `requests/${id}/`;
  const loadMessages = async () => setMessages(await allPages<Message>(`${path}messages/`, session.token));
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
      {!client && !frozen && <>
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
      <Text style={s.title}>Revisa el total antes de pagar</Text>
      <Text style={s.body}>Servicio: {money(bill.service_amount)}</Text>
      <Text style={s.body}>Materiales aprobados: {money(bill.materials_amount)}</Text>
      <Text style={s.heading}>{money(bill.total)}</Text>
      <Text style={s.body}>Neto: {money(bill.net_amount)} · IVA ilustrativo incluido ({bill.vat_percent}%): {money(bill.vat_amount)}</Text>
      <Text style={s.body}>Comisión FIX&GO ({bill.commission_percent}% del servicio): {money(bill.commission_amount)}. Incluida en el precio, no se suma al cliente.</Text>
      <Text style={s.body}>Para el prestador: {money(bill.provider_amount)}, incluidos materiales. Es un desglose de demostración, no una transferencia.</Text>
      <Text style={s.badge}>{{DRAFT:"Por confirmar", PENDING:"Demo pendiente", FAILED:"Demo rechazada", DEMO_PAID:"Demo aprobada",DEMO_REFUNDED:'Reembolsado · demo'}[bill.status]}</Text>
      <Text style={s.body}>Demostración académica: no se realiza ningún cobro real ni se genera una boleta tributaria. No ingreses datos de tarjetas.</Text>
      {!bill.demo_enabled && !paid && <Text style={s.body}>El pago de demostración está deshabilitado en este servidor.</Text>}
      {bill.has_pending_materials && <Text style={s.body}>Resuelve los materiales pendientes antes de confirmar el total.</Text>}
      {!paid&&!refunded&&<Text style={s.body}>Acepta la cotización y resuelve los materiales. Después paga la demostración para habilitar el chat y comenzar el trabajo.</Text>}
      {client && status === "ACCEPTED" && !frozen && <Button label="Confirmar total para demostración" busy={busy} disabled={!bill.demo_enabled || bill.has_pending_materials} onPress={() => void run(async () => {
        await api(`${path}checkout/`, session.token, "POST", {}); await refresh();
      })} />}
      {client && frozen && !paid && !refunded && bill.demo_enabled && <>
        <DemoWallet session={session} run={run} busy={busy}/>
        <Button label={bill.status === "FAILED" ? "Reintentar demo con aprobación" : "Simular pago aprobado"} busy={busy} onPress={() => void run(async () => {
          await api(`${path}payment/demo-result/`, session.token, "POST", {outcome:"approved"}); await refresh();
        })} />
        <Button secondary label="Simular rechazo de pago" busy={busy} onPress={() => void run(async () => {
          await api(`${path}payment/demo-result/`, session.token, "POST", {outcome:"rejected"}); await refresh();
        })} />
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
        {messages?.length === 0 && <Text style={s.body}>Todavía no hay mensajes.</Text>}
        {messages?.map(m => <View key={m.id} style={{padding:12, borderRadius:12, backgroundColor:m.sender_id === session.user.id ? "#FFF1BD" : "#EDF2F2", gap:4}}>
          <Text style={s.label}>{m.sender_id === session.user.id ? "Tú" : "La otra persona"} · {new Date(m.created_at).toLocaleString("es-CL")}</Text>
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
