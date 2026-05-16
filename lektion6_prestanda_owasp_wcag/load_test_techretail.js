/**
 * Övning 1 – Prestandatestning med k6
 * Lektion 6: Prestanda, Säkerhet & Tillgänglighetstest
 *
 * Kör: k6 run load_test_techretail.js
 * Snabbkörning: k6 run --vus 5 --duration 30s load_test_techretail.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

// === CUSTOM METRICS ===
// Rate spårar andel misslyckade anrop (felfrekvens)
const errorRate = new Rate("errors");
// Trend spårar svarstider för sökanrop specifikt
const searchDuration = new Trend("search_duration");

// === KONFIGURATION ===
export const options = {
  // Belastningsprofil: simulerar ett realistiskt trafikmönster
  // Ramp-up → Sustained load → Ramp-down
  stages: [
    { duration: "1m",   target: 50 }, // Ramp up: 0 → 50 användare på 1 minut
    { duration: "3m",   target: 50 }, // Håll: 50 användare i 3 minuter (peaktid)
    { duration: "1m",   target: 0  }, // Ramp down: 50 → 0 användare på 1 minut
  ],

  // Tröskelvärden — k6 returnerar exit code 99 om något bryts (bra för CI/CD)
  thresholds: {
    "http_req_duration": ["p(95)<500", "p(99)<1000"], // 95% av anrop < 500ms
    "errors":            ["rate<0.01"],                // Max 1% felfrekvens
    "search_duration":   ["p(95)<600"],                // Sökning: p95 < 600ms
  },
};

// === BASE URL ===
// k6.io:s publika test-API (gratis, ingen autentisering)
// I ett riktigt projekt: byt mot TechRetail AB:s staging-miljö
const BASE_URL = "https://test-api.k6.io";

// === HUVUDFUNKTION ===
// Varje virtuell användare (VU) kör denna funktion i en loop
export default function () {

  // --- Scenario 1: Hämta produktlista ---
  // Simulerar en kund som öppnar produktkatalogen
  const listResponse = http.get(`${BASE_URL}/public/crocodiles/`);

  const listOk = check(listResponse, {
    "produktlista: status är 200":    (r) => r.status === 200,
    "produktlista: svarstid < 500ms": (r) => r.timings.duration < 500,
    "produktlista: innehåller data":  (r) => r.body.length > 0,
  });

  // Registrera fel i custom metric (true = fel, false = ok)
  errorRate.add(!listOk);

  // --- Scenario 2: Hämta enskild produkt ---
  // Simulerar en kund som klickar på en specifik produkt
  const productResponse = http.get(`${BASE_URL}/public/crocodiles/1/`);

  const productOk = check(productResponse, {
    "produkt: status är 200":        (r) => r.status === 200,
    "produkt: innehåller name-fält": (r) => {
      try {
        const body = JSON.parse(r.body);
        return "name" in body;
      } catch {
        return false;
      }
    },
  });

  errorRate.add(!productOk);

  // --- Scenario 3: Simulera sökning ---
  // Simulerar en kund som söker efter produkter
  const searchStart = new Date().getTime();
  const searchResponse = http.get(`${BASE_URL}/public/crocodiles/?format=json`);
  const searchTime = new Date().getTime() - searchStart;

  // Spara söktiden i custom Trend-metric
  searchDuration.add(searchTime);

  const searchOk = check(searchResponse, {
    "sökning: status är 200": (r) => r.status === 200,
  });

  errorRate.add(!searchOk);

  // Simulera tänketid (1 sekund) — en riktig användare gör inte anrop direkt
  sleep(1);
}
