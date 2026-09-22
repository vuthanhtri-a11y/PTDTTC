const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const source = readFileSync(join(__dirname, '..', 'lt_backtest_scope.js'), 'utf8');
function run(res) {
  return JSON.parse(vm.runInNewContext(source, {
    window: { __W: { res, G: res.VNINDEX.c.length } },
  }));
}

test('filtered-universe backtest is unaffected by stocks that always fail Step 1', () => {
  const res = { VNINDEX: { c: Array.from({ length: 40 }, (_, t) => 100 * Math.exp(0.003 * t)) } };
  for (let i = 0; i < 35; i++) {
    res['S' + i] = { c: Array.from({ length: 40 }, (_, t) =>
      100 * Math.exp((0.006 + i * 0.0008) * t + (0.04 + i * 0.003) * Math.sin(t * 0.6 + i))) };
  }
  const baseline = run(res);
  for (let i = 0; i < 50; i++) {
    // The downtrend always fails the MA and 12-month relative-strength gates.
    res['FAIL' + i] = { c: Array.from({ length: 40 }, (_, t) =>
      100 * Math.exp(-0.06 * t + 0.09 * Math.sin(t * 0.6 + i))) };
  }
  const extended = run(res);
  assert.deepEqual(extended.CL_B1, baseline.CL_B1);
  assert.deepEqual(extended.CL_B2, baseline.CL_B2);
});

test('equal inputs are invariant to symbol insertion order', () => {
  const res = { VNINDEX: { c: Array.from({ length: 40 }, (_, t) => 100 + t) } };
  for (let i = 0; i < 15; i++) {
    res['S' + i] = { c: Array.from({ length: 40 }, (_, t) => 100 * Math.exp(t * 0.02)) };
  }
  const a = run(res);
  const b = run(Object.fromEntries(Object.entries(res).reverse()));
  assert.deepEqual(a.CL_B1, b.CL_B1);
  assert.deepEqual(a.CL_B2, b.CL_B2);
});

test('drawdown includes a loss in the first holding period', () => {
  const res = { VNINDEX: { c: Array(24).fill(100) } };
  for (let i = 0; i < 10; i++) {
    res['S' + i] = { c: Array.from({ length: 24 }, (_, t) => 100 * 0.9 ** t) };
  }
  const result = run(res).bo_loc_xu_huong;
  const net = (1 - 0.98 * 0.1) * (1 - 0.98 / 2 * 0.004) - 1;
  assert.equal(result.mdd, +net.toFixed(4));
});
