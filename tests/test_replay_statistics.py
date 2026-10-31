import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools'))
from replay_statistics import interval,seed_statistics,summarize

class StatisticsTests(unittest.TestCase):
 def test_interval_seed_units(self):
  a=interval(list(range(100)))
  self.assertEqual(a['mean'],49.5)
  self.assertAlmostEqual(a['high']-a['mean'],5.756509416710323,places=5)
  with self.assertRaises(ValueError): interval([0]*10000)
 def test_constant_interval(self):
  self.assertEqual(interval([2]*100),{'mean':2,'low':2,'high':2,'n':100})
 def records(self):
  rows=[]
  for f in range(1,101):
   for policy in ('random','guided'):
    # Relative advantages alternate 100% and 0%; ratio-of-means is not 50%.
    base=1 if f%2 else 10
    output=base*(2 if f%2 and policy=='guided' else 1)
    rows.append(dict(policy=policy,firm_id=f,round=1,technology=['Cobb-Douglas','Leontief','Linear','CES'][(f-1)%4],current_output=output,output_efficiency_pct=100 if policy=='guided' else 98))
  return rows
 def test_paired_percent_and_percentage_points(self):
  a=seed_statistics(self.records(),1)['All'][0]
  self.assertEqual(a['advantage'],50)
  self.assertEqual(a['d99'],100)
  self.assertEqual(a['r95'],100)
  self.assertEqual(a['d95'],0)
 def test_reject_incomplete_duplicate(self):
  rows=self.records()
  with self.assertRaises(ValueError):seed_statistics(rows[:-1],1)
  with self.assertRaises(ValueError):seed_statistics(rows[:-1]+[rows[0]],1)
 def test_summary_replication(self):
  a=seed_statistics(self.records(),1)
  self.assertEqual(summarize([a]*100,1)['All'][0]['advantage']['low'],50)
if __name__=='__main__':unittest.main()
