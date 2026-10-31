import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('builder',Path(__file__).parents[1]/'tools/build_replay_data.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ContractTests(unittest.TestCase):
 def row(self):
  values=['1','1','CES','.6','52','False','.5','50','2026','random','.6376','52.89','.1376','94.5'];return dict(zip(m.FIELDS,values))
 def test_false_is_false(self):self.assertIs(m.convert(self.row())['accepted'],False)
 def test_reject_bad_bool(self):
  r=self.row();r['accepted']='false'
  with self.assertRaises(ValueError):m.convert(r)
 def test_reject_nonfinite(self):
  r=self.row();r['current_output']='nan'
  with self.assertRaises(ValueError):m.convert(r)
 def test_reject_missing_column(self):
  r=self.row();del r['seed']
  with self.assertRaises(ValueError):m.convert(r)
if __name__=='__main__':unittest.main()
