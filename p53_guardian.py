import logging
import asyncio
import uuid
import hashlib
import json

class P53Guardian:
    def __init__(self, trinity_reference=None):
        self.logger = logging.getLogger("P53_GENOME_GUARD")
        self.trinity = trinity_reference
        self.integrity_threshold = 0.9
        self.hard_anomaly_limit = 0.5
        self.is_repairing = False
        self.repair_lock = asyncio.Lock()
        self.immune_memory = set()  # Base de anticorpos (Hashes SHA256)
        self.quarantine = []

    def get_fingerprint(self, data):
        """Gera um hash SHA256 estável e determinístico."""
        if not isinstance(data, dict):
            # Gera um hash a partir da string do dado para manter o determinismo
            return hashlib.sha256(str(data).encode()).hexdigest()

        # Normalização rigorosa: garante que a ordem das chaves não mude o Hash
        normalized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(normalized.encode()).hexdigest()

    def calculate_integrity(self, data):
        """Avaliação multinível da saúde dos dados/tarefa."""
        if not isinstance(data, dict):
            return 0.0

        fingerprint = self.get_fingerprint(data)

        # 1. Barreira Imunitária: Se o hash está na memória, bloqueia imediatamente
        if fingerprint in self.immune_memory:
            self.logger.warning(f"P53: Antígeno conhecido detectado [{fingerprint[:8]}]. Bloqueando...")
            return 0.0

        score = 1.0

        # 2. Filtro Ético Aura: Detecção de marcadores de "trevas" ou malícia
        intent = str(data.get("intent", "")).lower()
        dark_markers = ["malicious", "darkness", "harm", "exploit", "shadow"]

        if any(marker in intent for marker in dark_markers):
            score -= 0.8

        if data.get("status") == "corrupt":
            score -= 0.4

        return max(0.0, score)

    async def monitor_genetics(self, task_data):
        """Checkpoint G1: Verifica se a 'célula' pode avançar ou se deve parar."""
        score = self.calculate_integrity(task_data)

        if score < self.hard_anomaly_limit:
            self.logger.critical(f"P53: ANOMALIA CRÍTICA ({score}). Iniciando Arrest.")
            await self.trigger_arrest()
            await self.attempt_repair(task_data)
        elif score < self.integrity_threshold:
            self.logger.info(f"P53: Stress detectado ({score}). Notificando sistemas.")

    async def trigger_arrest(self):
        """Interrompe o ciclo de processamento para proteção."""
        self.logger.warning("P53: Ciclo suspenso. Isolando núcleo de processamento.")
        if self.trinity and hasattr(self.trinity, "is_running"):
            self.trinity.is_running = False

    async def attempt_repair(self, data):
        """Cura (limpeza) ou Apoptose (Isolamento na Quarentena)."""
        async with self.repair_lock:
            self.is_repairing = True
            try:
                fingerprint = self.get_fingerprint(data)
                score = self.calculate_integrity(data)

                if score < self.hard_anomaly_limit:
                    self.logger.critical("P53: Mutação maligna confirmada. Isolando na Quarentena.")
                    self.immune_memory.add(fingerprint)
                    
                    loop = asyncio.get_running_loop()
                    self.quarantine.append({
                        "id": str(uuid.uuid4()),
                        "fingerprint": fingerprint,
                        "timestamp": loop.time(),
                        "cell_data": data,
                    })
                else:
                    self.logger.info("P53: Reparação bem-sucedida. Reintegrando...")
            finally:
                if self.trinity and hasattr(self.trinity, "is_running"):
                    self.trinity.is_running = True
                self.is_repairing = False

    def safe_operation(self, *args, **kwargs):
        """Fallback: Operação genérica para manter o sistema rodando em caso de erro."""
        self.logger.warning("P53: Substituindo por linha genérica de segurança.")
        return None