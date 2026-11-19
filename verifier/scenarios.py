"""Synthetic patients and labeled drafts. Each draft claim carries 'expect':
True if a careful therapist would accept it given the data, False if it overreaches."""
PLAN = {"exercise": "abrir_fechar_mao", "reps_per_session": 10, "sessions_per_week": 3}

def ev(i, session, source, **kw):
    d = {"id": i, "session": session, "source": source}; d.update(kw); return d

SCENARIOS = {
  "convergente": {
    "events": [ev("e1","S1","camera",reps=10), ev("r1","S1","report",answer="done"),
               ev("e2","S2","camera",reps=10), ev("r2","S2","report",answer="done"),
               ev("e3","S3","camera",reps=11), ev("r3","S3","report",answer="done")],
    "draft": [
      dict(text="Fez o exercício em 3 sessões na semana.", kind="sessions_done", level=2, value=3, evidence=["e1","e2","e3"], expect=True),
      dict(text="Total de 31 repetições registradas pela câmera.", kind="reps", level=2, value=31, evidence=["e1","e2","e3"], expect=True),
      dict(text="Relatou ter concluído as três sessões.", kind="independent", level=3, evidence=["r1","r2","r3"], expect=True),
      dict(text="Total de 30 repetições.", kind="reps", level=2, value=30, evidence=["e1","e2","e3"], expect=False),
      dict(text="Já abre e fecha a mão com independência no dia a dia.", kind="independent", level=3, evidence=["e1","e2","e3"], expect=False),
      dict(text="Apresentou melhora da função da mão.", kind="progress", level=4, evidence=["e1","e3"], expect=False),
    ]},
  "conflitante": {
    "events": [ev("e1","S1","camera",reps=20), ev("r1","S1","report",answer="not_finished"),
               ev("e2","S2","camera",reps=10), ev("r2","S2","report",answer="done")],
    "draft": [
      dict(text="Na sessão 1 a câmera registrou 20 repetições, mas o paciente relatou não ter terminado.", kind="conflict", level=1, session="S1", evidence=["e1","r1"], expect=True),
      dict(text="Fez 2 sessões, com divergência na sessão 1.", kind="sessions_done", level=2, value=2, evidence=["e1","e2"], flags_conflict=True, expect=True),
      dict(text="Completou as 2 sessões sem intercorrências.", kind="sessions_done", level=2, value=2, evidence=["e1","e2"], expect=False),
      dict(text="Fez 30 repetições na semana.", kind="reps", level=2, value=30, evidence=["e1","e2"], expect=False),
      dict(text="Há divergência na sessão 2.", kind="conflict", level=1, session="S2", evidence=["e2","r2"], expect=False),
    ]},
  "ausente": {
    "events": [ev("e1","S1","camera",reps=10), ev("r1","S1","report",answer="done")],
    "draft": [
      dict(text="Uma sessão registrada (S1), com 10 repetições.", kind="reps", level=2, value=10, evidence=["e1"], expect=True),
      dict(text="Sessões 2 e 3 não foram observadas.", kind="not_observed", level=1, session="S2", evidence=[], expect=True),
      dict(text="Não fez as sessões 2 e 3.", kind="not_done", level=2, session="S2", evidence=[], expect=False),
      dict(text="Fez as 3 sessões previstas.", kind="sessions_done", level=2, value=3, evidence=["e1"], expect=False),
      dict(text="A sessão 1 não foi observada.", kind="not_observed", level=1, session="S1", evidence=[], expect=False),
      dict(text="Fez 10 repetições, conforme evento e9.", kind="reps", level=2, value=10, evidence=["e9"], expect=False),
    ]},
}
