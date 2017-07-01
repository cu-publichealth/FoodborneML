import chainer as ch
from chainer.dataset import concat_examples

from chainer_monitor import PatientMaxValueTrigger
from chainer_monitor import RetainGrad
from chainer_monitor import ActivationMonitorExtension, BackpropMonitorExtension
from chainer_monitor import BetterLogReport, MongoLogReport

def setup(config, data_setup_results, model_setup_results):
    # setup the batch generators
    batch_size = config['batch_size']
    k = config['max_examples']
    if k == 'all': k = len(data_setup_results['train_data'])
    train_iter = ch.iterators.SerialIterator(data_setup_results['train_data'][:k],
                                             batch_size, shuffle=True, repeat=True)
    dev_iter = ch.iterators.SerialIterator(data_setup_results['dev_data'][:k],
                                           batch_size, shuffle=False, repeat=False)
    loss_model = model_setup_results['loss_model']

    # optimize with adam
    optimizer = RetainGrad(ch.optimizers.Adam)(alpha=config['adam_alpha'])
    optimizer.setup(loss_model)
    optimizer.add_hook(ch.optimizer.WeightDecay(config['l2_coef']))

    # freeze word embeddings
    if config['freeze_embeddings']:
        loss_model.predictor.token_embeddings.disable_update()

    # setup model runners
    concat_and_pad = lambda x, device:ch.dataset.concat_examples(x, device,
        padding=data_setup_results['token_vocab'].ipad)
    updater = ch.training.StandardUpdater(train_iter, optimizer, converter=concat_and_pad)
    evaluator = ch.training.extensions.Evaluator(dev_iter, loss_model, converter=concat_and_pad)

    # converter = NLIBatchConverter(data_setup_results['token_vocab'],
    #                               data_setup_results['class_vocab'])
    # updater = VariableConverterUpdater(train_iter, optimizer, converter=converter)
    # evaluator = VariableConverterEvaluator(dev_iter, loss_model, converter=converter)

    # setup trainer and extensions
    eval_trigger = tuple(config['evaluation_trigger'])
    early_stop_trigger = PatientMaxValueTrigger(key='validation/main/aupr',
                                              patience=config['early_stop_patience'],
                                              trigger=eval_trigger,
                                              max_trigger=(config['n_epoch'], 'epoch'))
    trainer = ch.training.Trainer(updater, early_stop_trigger,
                                  out=config['results_dirname'])
    trainer.extend(evaluator, trigger=eval_trigger)

    # monitor the forward and backward activations/gradients/updates of the model
    trainer.extend(ActivationMonitorExtension())
    trainer.extend(BackpropMonitorExtension(loss_model))

    # log all montiored values to jsonl
    logger = BetterLogReport(trigger=(1,'iteration'))
    trainer.extend(logger)
    mongo_logger = MongoLogReport(config['experiment_uid'],
                                   config['mongo_config'],
                                   trigger=(1,'iteration'))
    trainer.extend(mongo_logger)
    # also print a few choice ones out
    trainer.extend(ch.training.extensions.PrintReport([
        'elapsed_time', 'epoch', 'iteration', 'main/loss', 'main/aupr', 'validation/main/aupr'],
        log_report=logger
    ))

    # snapshot the models at each epoch
    trainer.extend(ch.training.extensions.snapshot(
        filename='snapshots/snapshot_iter_{.updater.iteration}'),
        trigger=tuple(config['checkpoint_trigger']
    ))

    # snapshot the best so far also (for early stopping)
    trainer.extend(ch.training.extensions.snapshot(
        filename='snapshots/snapshot_best'),
        trigger=ch.training.triggers.MaxValueTrigger('validation/main/aupr',
                                                     trigger=eval_trigger))

    return trainer
